"""Evaluation service for scoring conversations against criteria.

Uses LLM-based evaluation to assess conversation quality.
"""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from langchain.schema import HumanMessage
from sqlalchemy.orm import Session

from ..models.conversation import ConversationORM
from ..models.evaluation_criterion import EvaluationCriterionORM
from ..models.evaluation_result import EvaluationResultORM
from ..models.iteration import IterationORM
from ..models.project import ProjectORM
from ..services.llm_factory import get_llm_client


class ConversationEvaluator:
    """Service for evaluating conversations against criteria."""

    def __init__(self, db_session: Session):
        """Initialize evaluator.

        Args:
            db_session: Database session for persistence
        """
        self.db = db_session

    async def evaluate_iteration(
        self,
        iteration: IterationORM,
        project: ProjectORM,
        conversations: list[ConversationORM],
    ) -> EvaluationResultORM:
        """Evaluate all conversations in an iteration.

        Args:
            iteration: Iteration being evaluated
            project: Project context
            conversations: List of conversations to evaluate

        Returns:
            Evaluation result with criterion scores
        """
        start_time = datetime.utcnow()

        # Get evaluator LLM (use GPT-4 for reliable evaluation)
        evaluator_llm = get_llm_client("openai", "gpt-4", temperature=0.3, max_tokens=2000)

        # Evaluate each criterion across all conversations
        criterion_scores: dict[str, dict[str, any]] = {}
        criteria = project.evaluation_criteria

        for criterion in criteria:
            # Aggregate scores across all conversations
            conversation_scores = []

            for conversation in conversations:
                score = await self._evaluate_criterion(
                    evaluator_llm,
                    criterion,
                    conversation,
                )
                conversation_scores.append(score)

            # Average score across conversations
            avg_score = sum(s["score"] for s in conversation_scores) / len(
                conversation_scores
            )
            explanations = [s["explanation"] for s in conversation_scores]

            criterion_scores[criterion.id] = {
                "score": round(avg_score, 2),
                "explanation": " | ".join(explanations),
                "passed": avg_score >= criterion.threshold,
            }

        # Calculate aggregate metrics
        all_scores = [data["score"] for data in criterion_scores.values()]
        aggregate_score = round(sum(all_scores) / len(all_scores), 2)

        # Check if all criteria passed
        all_passed = all(data["passed"] for data in criterion_scores.values())

        # Calculate duration
        end_time = datetime.utcnow()
        duration = int((end_time - start_time).total_seconds())

        # Create evaluation result
        result = EvaluationResultORM(
            iteration_id=iteration.id,
            criterion_scores=criterion_scores,
            aggregate_score=aggregate_score,
            passed=all_passed,
            evaluator_model="gpt-4",
            evaluation_duration_seconds=duration,
        )

        self.db.add(result)
        self.db.commit()

        return result

    async def _evaluate_criterion(
        self,
        llm,
        criterion: EvaluationCriterionORM,
        conversation: ConversationORM,
    ) -> dict[str, any]:
        """Evaluate a single criterion for one conversation.

        Args:
            llm: Evaluator LLM client
            criterion: Evaluation criterion
            conversation: Conversation to evaluate

        Returns:
            Dict with score (0-100) and explanation
        """
        # Build evaluation prompt
        prompt_parts = [
            f"Evaluate this conversation on: {criterion.name}",
            f"\nDescription: {criterion.description}",
        ]

        if criterion.scoring_rubric:
            prompt_parts.append(f"\nScoring Rubric:\n{criterion.scoring_rubric}")

        prompt_parts.append("\nConversation:")
        for turn in conversation.turns:
            prompt_parts.append(f"User: {turn['user_message']}")
            prompt_parts.append(f"Assistant: {turn['assistant_message']}")

        prompt_parts.append(
            "\nProvide your evaluation as JSON with this exact structure:"
            '\n{"score": <number 0-100>, "explanation": "<brief explanation>"}'
        )

        prompt = "\n".join(prompt_parts)
        messages = [HumanMessage(content=prompt)]

        response = await llm.ainvoke(messages)
        response_text = response.content.strip()

        # Parse JSON response
        try:
            # Extract JSON from response (may have markdown code blocks)
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            result = json.loads(json_str)

            # Validate structure
            if "score" not in result or "explanation" not in result:
                raise ValueError("Missing required fields")

            # Clamp score to 0-100
            result["score"] = max(0, min(100, float(result["score"])))

            return result

        except Exception as e:
            # Fallback to parsing score from text
            return {
                "score": 50.0,  # Neutral score on parse failure
                "explanation": f"Evaluation parse error: {str(e)}. Raw response: {response_text[:200]}",
            }

    def get_evaluation_result(
        self, iteration_id: UUID
    ) -> Optional[EvaluationResultORM]:
        """Get evaluation result for an iteration.

        Args:
            iteration_id: Iteration UUID

        Returns:
            Evaluation result or None
        """
        return (
            self.db.query(EvaluationResultORM)
            .filter(EvaluationResultORM.iteration_id == str(iteration_id))
            .first()
        )
