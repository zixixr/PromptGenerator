"""LLM provider factory with retry logic and credential management.

Provides unified interface to multiple LLM providers.
"""

from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from ..storage.encryption import get_encryption_service


class LLMFactory:
    """Factory for creating LLM clients with proper credentials."""

    def __init__(self):
        """Initialize LLM factory."""
        self.encryption = get_encryption_service()

    def create_client(
        self,
        provider: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> BaseChatModel:
        """Create an LLM client for the specified provider.

        Args:
            provider: Provider name (openai, anthropic, google, custom)
            model_name: Model identifier
            temperature: Sampling temperature (0-2)
            max_tokens: Max tokens to generate

        Returns:
            Configured LLM client

        Raises:
            ValueError: If provider is unsupported or credentials missing
        """
        provider = provider.lower()

        if provider == "openai":
            return self._create_openai_client(model_name, temperature, max_tokens)
        elif provider == "anthropic":
            return self._create_anthropic_client(model_name, temperature, max_tokens)
        elif provider == "google":
            return self._create_google_client(model_name, temperature, max_tokens)
        elif provider == "custom":
            return self._create_custom_client(model_name, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _create_openai_client(
        self, model_name: str, temperature: float, max_tokens: Optional[int]
    ) -> BaseChatModel:
        """Create OpenAI client.

        Args:
            model_name: OpenAI model name
            temperature: Temperature setting
            max_tokens: Max tokens

        Returns:
            Configured ChatOpenAI client
        """
        api_key = self.encryption.retrieve_credential("openai")
        if not api_key:
            raise ValueError("OpenAI API key not configured. Use /api/credentials to set it.")

        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "api_key": api_key,
            "request_timeout": 60,
            "max_retries": 3,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        return ChatOpenAI(**kwargs)

    def _create_anthropic_client(
        self, model_name: str, temperature: float, max_tokens: Optional[int]
    ) -> BaseChatModel:
        """Create Anthropic client.

        Args:
            model_name: Anthropic model name
            temperature: Temperature setting
            max_tokens: Max tokens

        Returns:
            Configured ChatAnthropic client
        """
        api_key = self.encryption.retrieve_credential("anthropic")
        if not api_key:
            raise ValueError("Anthropic API key not configured. Use /api/credentials to set it.")

        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "anthropic_api_key": api_key,
            "timeout": 60,
            "max_retries": 3,
        }

        if max_tokens:
            kwargs["max_tokens_to_sample"] = max_tokens

        return ChatAnthropic(**kwargs)

    def _create_google_client(
        self, model_name: str, temperature: float, max_tokens: Optional[int]
    ) -> BaseChatModel:
        """Create Google client.

        Args:
            model_name: Google model name
            temperature: Temperature setting
            max_tokens: Max tokens

        Returns:
            Configured ChatGoogleGenerativeAI client
        """
        api_key = self.encryption.retrieve_credential("google")
        if not api_key:
            raise ValueError("Google API key not configured. Use /api/credentials to set it.")

        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "google_api_key": api_key,
        }

        if max_tokens:
            kwargs["max_output_tokens"] = max_tokens

        return ChatGoogleGenerativeAI(**kwargs)

    def _create_custom_client(
        self, model_name: str, temperature: float, max_tokens: Optional[int]
    ) -> BaseChatModel:
        """Create custom OpenAI-compatible client.

        Args:
            model_name: Model identifier
            temperature: Temperature setting
            max_tokens: Max tokens

        Returns:
            Configured ChatOpenAI client with custom base_url
        """
        # Retrieve custom endpoint configuration
        api_key = self.encryption.retrieve_credential("custom_api_key")
        base_url = self.encryption.retrieve_credential("custom_base_url")

        if not api_key or not base_url:
            raise ValueError(
                "Custom endpoint not configured. Set custom_api_key and custom_base_url."
            )

        kwargs = {
            "model": model_name,
            "temperature": temperature,
            "api_key": api_key,
            "base_url": base_url,
            "request_timeout": 60,
            "max_retries": 3,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        return ChatOpenAI(**kwargs)


# Global factory instance
_llm_factory: Optional[LLMFactory] = None


def get_llm_factory() -> LLMFactory:
    """Get global LLM factory instance.

    Returns:
        Singleton LLMFactory instance
    """
    global _llm_factory
    if _llm_factory is None:
        _llm_factory = LLMFactory()
    return _llm_factory


def get_llm_client(
    provider: str,
    model_name: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> BaseChatModel:
    """Convenience function to get an LLM client.

    Args:
        provider: Provider name
        model_name: Model identifier
        temperature: Sampling temperature
        max_tokens: Max tokens to generate

    Returns:
        Configured LLM client
    """
    factory = get_llm_factory()
    return factory.create_client(provider, model_name, temperature, max_tokens)
