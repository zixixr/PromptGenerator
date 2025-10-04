"""Conversation simulator service.

Orchestrates multi-turn conversations between system prompt and simulated user.
"""

from typing import Optional
from uuid import UUID

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from sqlalchemy.orm import Session

from ..models.conversation import ConversationORM, ConversationStatus, ConversationTurn
from ..models.project import ProjectORM
from ..models.test_scenario import TestScenarioORM
from ..services.llm_factory import get_llm_client


class ConversationSimulator:
    """Service for simulating multi-turn conversations."""

    def __init__(self, db_session: Session):
        """Initialize conversation simulator.

        Args:
            db_session: Database session for persistence
        """
        self.db = db_session

    async def simulate_conversation(
        self,
        project: ProjectORM,
        test_scenario: TestScenarioORM,
        system_prompt: str,
        iteration_id: UUID,
    ) -> ConversationORM:
        """Simulate a multi-turn conversation for a test scenario.

        Args:
            project: Project being optimized
            test_scenario: Test scenario to simulate
            system_prompt: Current system prompt to evaluate
            iteration_id: Iteration this conversation belongs to

        Returns:
            Created conversation record with all turns
        """
        # Get LLM clients
        target_llm = get_llm_client(
            project.model_configuration.provider,
            project.model_configuration.model_name,
            project.model_configuration.temperature,
            project.model_configuration.max_tokens,
        )

        user_simulator_llm = get_llm_client(
            "openai", "gpt-4", temperature=0.8, max_tokens=500
        )

        # Create conversation record
        conversation = ConversationORM(
            iteration_id=str(iteration_id),
            test_scenario_id=test_scenario.id,
            status=ConversationStatus.RUNNING,
            turns=[],
        )
        self.db.add(conversation)
        self.db.flush()

        try:
            # Initialize conversation history
            turns: list[ConversationTurn] = []
            messages = [SystemMessage(content=system_prompt)]

            # Simulate turns up to turn_limit
            for turn_num in range(1, test_scenario.turn_limit + 1):
                # Generate user message
                user_message = await self._generate_user_message(
                    user_simulator_llm,
                    test_scenario,
                    turns,
                    turn_num,
                )

                messages.append(HumanMessage(content=user_message))

                # Get assistant response
                assistant_response = await target_llm.ainvoke(messages)
                assistant_message = assistant_response.content

                messages.append(AIMessage(content=assistant_message))

                # Record turn
                turn = ConversationTurn(
                    turn_number=turn_num,
                    user_message=user_message,
                    assistant_message=assistant_message,
                )
                turns.append(turn)

            # Update conversation with completed turns
            conversation.turns = [turn.model_dump() for turn in turns]
            conversation.status = ConversationStatus.COMPLETED
            self.db.commit()

            return conversation

        except Exception as e:
            # Mark conversation as failed
            conversation.status = ConversationStatus.FAILED
            conversation.turns = [turn.model_dump() for turn in turns]
            self.db.commit()
            raise RuntimeError(
                f"Conversation simulation failed at turn {len(turns)}: {str(e)}"
            ) from e

    async def _generate_user_message(
        self,
        llm: BaseChatModel,
        test_scenario: TestScenarioORM,
        previous_turns: list[ConversationTurn],
        turn_number: int,
    ) -> str:
        """Generate a realistic user message for the scenario.

        Args:
            llm: LLM client for user simulation
            test_scenario: Test scenario context
            previous_turns: Previously completed turns
            turn_number: Current turn number

        Returns:
            Generated user message
        """
        # Build context for user simulator
        context_parts = [
            f"You are simulating a user in this scenario: {test_scenario.description}",
            f"This is turn {turn_number} of {test_scenario.turn_limit}.",
        ]

        if previous_turns:
            context_parts.append("\nPrevious conversation:")
            for turn in previous_turns:
                context_parts.append(f"User: {turn.user_message}")
                context_parts.append(f"Assistant: {turn.assistant_message}")

        context_parts.append(
            "\nGenerate the next user message. Be realistic and natural. "
            "Respond with ONLY the user message, no meta-commentary."
        )

        prompt = "\n".join(context_parts)
        messages = [HumanMessage(content=prompt)]

        response = await llm.ainvoke(messages)
        return response.content.strip()

    def get_conversation_by_id(self, conversation_id: UUID) -> Optional[ConversationORM]:
        """Retrieve a conversation by ID.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Conversation record or None if not found
        """
        return (
            self.db.query(ConversationORM)
            .filter(ConversationORM.id == str(conversation_id))
            .first()
        )
