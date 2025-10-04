"""Iteration orchestrator service.

Coordinates the full optimization loop: simulate, evaluate, rewrite, iterate.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.iteration import IterationORM, IterationStatus
from ..models.project import ProjectORM, ProjectStatus
from ..models.prompt import PromptORM
from ..services.evaluator import ConversationEvaluator
from ..services.rewriter import PromptRewriter
from ..services.simulator import ConversationSimulator


class IterationOrchestrator:
    """Service for orchestrating the optimization iteration loop."""

    def __init__(self, db_session: Session):
        """Initialize orchestrator.

        Args:
            db_session: Database session
        """
        self.db = db_session
        self.simulator = ConversationSimulator(db_session)
        self.evaluator = ConversationEvaluator(db_session)
        self.rewriter = PromptRewriter(db_session)

    async def run_iteration(
        self, project: ProjectORM, prompt: PromptORM, iteration_number: int
    ) -> tuple[IterationORM, Optional[PromptORM]]:
        """Run a single optimization iteration.

        Args:
            project: Project being optimized
            prompt: Current prompt to evaluate
            iteration_number: Iteration number (1-indexed)

        Returns:
            Tuple of (iteration_record, next_prompt_or_none)
            next_prompt is None if optimization succeeded (all criteria passed)
        """
        start_time = datetime.utcnow()

        # Create iteration record
        iteration = IterationORM(
            project_id=project.id,
            prompt_id=prompt.id,
            iteration_number=iteration_number,
            status=IterationStatus.RUNNING,
            started_at=start_time,
        )
        self.db.add(iteration)
        self.db.flush()

        try:
            # Step 1: Simulate conversations for all test scenarios
            conversations = []
            for scenario in project.test_scenarios:
                conv = await self.simulator.simulate_conversation(
                    project=project,
                    test_scenario=scenario,
                    system_prompt=prompt.content,
                    iteration_id=UUID(iteration.id),
                )
                conversations.append(conv)

            # Step 2: Evaluate all conversations
            evaluation_result = await self.evaluator.evaluate_iteration(
                iteration=iteration,
                project=project,
                conversations=conversations,
            )

            # Step 3: Update iteration with results
            end_time = datetime.utcnow()
            duration = int((end_time - start_time).total_seconds())

            passed_count = sum(
                1
                for scores in evaluation_result.criterion_scores.values()
                if scores["passed"]
            )
            total_count = len(evaluation_result.criterion_scores)

            iteration.passed_criteria_count = passed_count
            iteration.failed_criteria_count = total_count - passed_count
            iteration.all_criteria_passed = evaluation_result.passed
            iteration.completed_at = end_time
            iteration.duration_seconds = duration
            iteration.status = IterationStatus.COMPLETED

            self.db.commit()

            # Step 4: Decide next action
            if evaluation_result.passed:
                # Success! No rewrite needed
                return iteration, None
            else:
                # Failure: rewrite prompt for next iteration
                next_prompt = await self.rewriter.rewrite_prompt(
                    project=project,
                    current_prompt=prompt,
                    evaluation_result=evaluation_result,
                )
                return iteration, next_prompt

        except Exception as e:
            # Mark iteration as failed
            iteration.status = IterationStatus.FAILED
            iteration.completed_at = datetime.utcnow()
            self.db.commit()
            raise RuntimeError(f"Iteration {iteration_number} failed: {str(e)}") from e

    async def run_optimization(self, project_id: UUID) -> ProjectORM:
        """Run full optimization loop until success or max iterations.

        Args:
            project_id: Project UUID to optimize

        Returns:
            Updated project record
        """
        # Load project
        project = self.db.query(ProjectORM).filter(ProjectORM.id == str(project_id)).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Validate project is ready
        if project.status != ProjectStatus.DRAFT:
            raise ValueError(f"Project must be in DRAFT status, found {project.status}")

        if not project.test_scenarios:
            raise ValueError("Project must have at least one test scenario")

        if not project.evaluation_criteria:
            raise ValueError("Project must have at least one evaluation criterion")

        # Update project status
        project.status = ProjectStatus.RUNNING
        self.db.commit()

        try:
            # Get initial prompt (latest or create from project.initial_prompt)
            current_prompt = self._get_or_create_initial_prompt(project)

            iteration_num = 1
            max_iterations = project.max_iterations

            while iteration_num <= max_iterations:
                # Run iteration
                iteration, next_prompt = await self.run_iteration(
                    project=project,
                    prompt=current_prompt,
                    iteration_number=iteration_num,
                )

                # Check if optimization succeeded
                if next_prompt is None:
                    # Success!
                    project.status = ProjectStatus.COMPLETED
                    self.db.commit()
                    return project

                # Prepare for next iteration
                current_prompt = next_prompt
                iteration_num += 1

            # Reached max iterations without success
            project.status = ProjectStatus.FAILED
            self.db.commit()
            return project

        except Exception as e:
            # Mark project as failed
            project.status = ProjectStatus.FAILED
            self.db.commit()
            raise RuntimeError(f"Optimization failed: {str(e)}") from e

    def _get_or_create_initial_prompt(self, project: ProjectORM) -> PromptORM:
        """Get latest prompt or create initial one.

        Args:
            project: Project context

        Returns:
            Latest prompt or newly created initial prompt
        """
        from ..models.prompt import GenerationMethod

        # Check if prompts already exist
        existing = (
            self.db.query(PromptORM)
            .filter(PromptORM.project_id == project.id)
            .order_by(PromptORM.created_at.desc())
            .first()
        )

        if existing:
            return existing

        # Create initial prompt from project.initial_prompt
        initial_prompt = PromptORM(
            project_id=project.id,
            content=project.initial_prompt,
            parent_id=None,
            generation_method=GenerationMethod.INITIAL,
            rewrite_rationale=None,
            created_at=datetime.utcnow(),
        )

        self.db.add(initial_prompt)
        self.db.commit()

        return initial_prompt

    def get_iteration_by_id(self, iteration_id: UUID) -> Optional[IterationORM]:
        """Get iteration by ID.

        Args:
            iteration_id: Iteration UUID

        Returns:
            Iteration record or None
        """
        return (
            self.db.query(IterationORM)
            .filter(IterationORM.id == str(iteration_id))
            .first()
        )

    def get_project_iterations(self, project_id: UUID) -> list[IterationORM]:
        """Get all iterations for a project.

        Args:
            project_id: Project UUID

        Returns:
            List of iterations in chronological order
        """
        return (
            self.db.query(IterationORM)
            .filter(IterationORM.project_id == str(project_id))
            .order_by(IterationORM.iteration_number)
            .all()
        )
