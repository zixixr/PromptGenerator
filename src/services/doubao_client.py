import logging
from typing import List, Dict
from openai import OpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Raised when Doubao API rate limit is exceeded."""
    pass


class ServiceUnavailable(Exception):
    """Raised when Doubao API is unavailable."""
    pass


class DoubaoClient:
    """Async client for Doubao Seed 1.6 API using OpenAI SDK."""

    def __init__(self, api_key: str = None, endpoint: str = None, model: str = None):
        self.api_key = api_key or settings.ARK_API_KEY
        self.endpoint = endpoint or settings.DOUBAO_API_ENDPOINT
        self.model = model or settings.DOUBAO_MODEL
        
        # Initialize OpenAI client with Ark endpoint
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.api_key,
        )
        self.timeout = 6.0  # 6 second timeout for first token

    async def send_message(
        self, system_prompt: str, context: List[Dict], user_message: str, timeout: int = 6
    ) -> str:
        """
        Send message to Doubao API with context.

        Args:
            system_prompt: Resolved system prompt
            context: List of previous message rounds
            user_message: New user message
            timeout: Timeout in seconds (default 6)

        Returns:
            Assistant response string

        Raises:
            RateLimitExceeded: When API returns 429
            ServiceUnavailable: When API is unreachable or times out
        """
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context)
        messages.append({"role": "user", "content": user_message})

        try:
            # Call OpenAI-compatible API (synchronous in async function)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                timeout=timeout,
            )

            # Extract assistant response
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                logger.error(f"Unexpected API response format: {response}")
                return "Error: Unable to generate response"

        except Exception as e:
            error_msg = str(e)
            
            # Check for rate limit
            if "429" in error_msg or "rate limit" in error_msg.lower():
                logger.warning("Doubao API rate limit exceeded")
                raise RateLimitExceeded("Rate limit exceeded, please try again later")
            
            # Check for timeout
            if "timeout" in error_msg.lower():
                logger.error("Doubao API request timed out")
                raise ServiceUnavailable("Request timed out after 6 seconds")
            
            # Generic error
            logger.error(f"Doubao API error: {e}")
            raise ServiceUnavailable(f"API error: {str(e)}")
