"""Prompt rewriter service.

Automatically rewrites system prompts based on evaluation failures.
"""

from datetime import datetime
from uuid import UUID

from langchain.schema import HumanMessage
from sqlalchemy.orm import Session

from ..models.evaluation_result import EvaluationResultORM
from ..models.prompt import GenerationMethod, PromptORM
from ..models.project import ProjectORM
from ..services.llm_factory import get_llm_client


class PromptRewriter:
    """Service for rewriting prompts based on evaluation feedback."""

    def __init__(self, db_session: Session):
        """Initialize rewriter.

        Args:
            db_session: Database session for persistence
        """
        self.db = db_session

    async def rewrite_prompt(
        self,
        project: ProjectORM,
        current_prompt: PromptORM,
        evaluation_result: EvaluationResultORM,
    ) -> PromptORM:
        """Rewrite a prompt to address evaluation failures.

        Args:
            project: Project context
            current_prompt: Current prompt being optimized
            evaluation_result: Evaluation result with failures

        Returns:
            New rewritten prompt
        """
        # Get rewriter LLM (use GPT-4 for better reasoning)
        rewriter_llm = get_llm_client("openai", "gpt-4", temperature=0.7, max_tokens=1500)

        # Build rewriting instructions
        prompt_parts = [
            "You are a prompt engineering expert. Rewrite the following system prompt to improve its performance.",
            f"\nCurrent System Prompt:\n{current_prompt.content}",
            "\nEvaluation Results:",
        ]

        # Add failed criteria details
        failed_criteria = []
        for criterion_id, scores in evaluation_result.criterion_scores.items():
            if not scores["passed"]:
                criterion = self._get_criterion_by_id(project, criterion_id)
                failed_criteria.append(
                    {
                        "name": criterion.name,
                        "description": criterion.description,
                        "threshold": criterion.threshold,
                        "score": scores["score"],
                        "explanation": scores["explanation"],
                    }
                )

        for fc in failed_criteria:
            prompt_parts.append(
                f"\n- {fc['name']}: Scored {fc['score']}/{fc['threshold']} (FAILED)"
            )
            prompt_parts.append(f"  Description: {fc['description']}")
            prompt_parts.append(f"  Feedback: {fc['explanation']}")

        prompt_parts.append(
            "\nRewrite the system prompt to specifically address these failures. "
            "Maintain the core purpose but adjust tone, instructions, or constraints as needed. "
            "Respond with ONLY the rewritten prompt, no meta-commentary or explanations."
        )

        prompt = "\n".join(prompt_parts)
        messages = [HumanMessage(content=prompt)]

        response = await rewriter_llm.ainvoke(messages)
        new_content = response.content.strip()

        # Create rationale explaining the rewrite
        rationale = self._generate_rationale(failed_criteria)

        # Create new prompt version
        new_prompt = PromptORM(
            project_id=project.id,
            content=new_content,
            parent_id=current_prompt.id,
            generation_method=GenerationMethod.LLM_REWRITE,
            rewrite_rationale=rationale,
            created_at=datetime.utcnow(),
        )

        self.db.add(new_prompt)
        self.db.commit()

        return new_prompt

    def _get_criterion_by_id(
        self, project: ProjectORM, criterion_id: str
    ) -> any:
        """Get criterion by ID from project.

        Args:
            project: Project containing criteria
            criterion_id: Criterion UUID

        Returns:
            Criterion object
        """
        for criterion in project.evaluation_criteria:
            if criterion.id == criterion_id:
                return criterion
        raise ValueError(f"Criterion {criterion_id} not found in project")

    def _generate_rationale(self, failed_criteria: list[dict]) -> str:
        """Generate human-readable rationale for rewrite.

        Args:
            failed_criteria: List of failed criterion details

        Returns:
            Rationale string
        """
        if not failed_criteria:
            return "Manual rewrite with no specific failures"

        parts = ["Rewritten to address:"]
        for fc in failed_criteria:
            parts.append(
                f"- {fc['name']}: score {fc['score']} below threshold {fc['threshold']}"
            )

        return " ".join(parts)

    async def manual_edit_prompt(
        self, project: ProjectORM, parent_prompt: PromptORM, new_content: str
    ) -> PromptORM:
        """Create a manually edited prompt version.

        Args:
            project: Project context
            parent_prompt: Parent prompt being edited
            new_content: New prompt content

        Returns:
            New prompt version
        """
        new_prompt = PromptORM(
            project_id=project.id,
            content=new_content,
            parent_id=parent_prompt.id,
            generation_method=GenerationMethod.MANUAL_EDIT,
            rewrite_rationale="Manual edit by user",
            created_at=datetime.utcnow(),
        )

        self.db.add(new_prompt)
        self.db.commit()

        return new_prompt

    def get_prompt_lineage(self, prompt_id: UUID) -> list[PromptORM]:
        """Get lineage of prompts from initial to current.

        Args:
            prompt_id: Current prompt UUID

        Returns:
            List of prompts in chronological order
        """
        lineage = []
        current = self.db.query(PromptORM).filter(PromptORM.id == str(prompt_id)).first()

        while current:
            lineage.insert(0, current)
            if current.parent_id:
                current = (
                    self.db.query(PromptORM)
                    .filter(PromptORM.id == current.parent_id)
                    .first()
                )
            else:
                break

        return lineage
