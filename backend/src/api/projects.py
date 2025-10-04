"""Projects API routes.

Handles project CRUD operations, iteration execution, and export.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..models.project import Project, ProjectCreate, ProjectORM, ProjectResponse
from ..services.orchestrator import IterationOrchestrator
from ..storage.db import get_session

router = APIRouter()


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_session),
) -> ProjectResponse:
    """Create a new optimization project.

    Args:
        project: Project creation data
        db: Database session

    Returns:
        Created project with generated ID
    """
    # Create project ORM instance
    project_orm = ProjectORM(**project.model_dump())

    db.add(project_orm)
    db.commit()
    db.refresh(project_orm)

    return ProjectResponse.model_validate(project_orm)


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by project status"),
    db: Session = Depends(get_session),
) -> list[ProjectResponse]:
    """List all projects with optional status filter.

    Args:
        status: Optional status filter
        db: Database session

    Returns:
        List of projects
    """
    query = db.query(ProjectORM)

    if status:
        query = query.filter(ProjectORM.status == status)

    projects = query.order_by(ProjectORM.created_at.desc()).all()

    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: Session = Depends(get_session),
) -> ProjectResponse:
    """Get a single project by ID.

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    project = db.query(ProjectORM).filter(ProjectORM.id == str(project_id)).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    return ProjectResponse.model_validate(project)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: Session = Depends(get_session),
) -> None:
    """Delete a project and all related data.

    Args:
        project_id: Project UUID
        db: Database session

    Raises:
        HTTPException: If project not found
    """
    project = db.query(ProjectORM).filter(ProjectORM.id == str(project_id)).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    db.delete(project)
    db.commit()


@router.post("/projects/{project_id}/iterations", status_code=202)
async def start_optimization(
    project_id: UUID,
    db: Session = Depends(get_session),
) -> dict[str, str]:
    """Start optimization for a project.

    This is an async operation that will run iterations until
    all criteria pass or max iterations is reached.

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        Status message

    Raises:
        HTTPException: If project not found or invalid state
    """
    project = db.query(ProjectORM).filter(ProjectORM.id == str(project_id)).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # Start orchestration (this is async in production, here it runs synchronously)
    try:
        orchestrator = IterationOrchestrator(db)
        await orchestrator.run_optimization(project_id)

        return {
            "status": "started",
            "message": f"Optimization started for project {project_id}",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/projects/{project_id}/export")
async def export_project(
    project_id: UUID,
    format: str = Query("json", description="Export format: json or csv"),
    db: Session = Depends(get_session),
) -> dict:
    """Export optimization results.

    Args:
        project_id: Project UUID
        format: Export format (json or csv)
        db: Database session

    Returns:
        Export data

    Raises:
        HTTPException: If project not found or format unsupported
    """
    project = db.query(ProjectORM).filter(ProjectORM.id == str(project_id)).first()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    # Build export data
    export_data = {
        "project": ProjectResponse.model_validate(project).model_dump(),
        "iterations": [],
        "final_prompt": None,
    }

    # Add iterations data
    for iteration in project.iterations:
        iteration_data = {
            "iteration_number": iteration.iteration_number,
            "status": iteration.status,
            "passed_criteria_count": iteration.passed_criteria_count,
            "failed_criteria_count": iteration.failed_criteria_count,
            "duration_seconds": iteration.duration_seconds,
        }
        export_data["iterations"].append(iteration_data)

    # Get final optimized prompt
    if project.iterations:
        last_iteration = sorted(project.iterations, key=lambda i: i.iteration_number)[-1]
        if last_iteration.prompt:
            export_data["final_prompt"] = {
                "content": last_iteration.prompt.content,
                "generation_method": last_iteration.prompt.generation_method,
                "rewrite_rationale": last_iteration.prompt.rewrite_rationale,
            }

    if format == "json":
        return export_data
    else:
        # CSV format (simplified)
        import io
        import csv

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["Iteration", "Status", "Passed", "Failed", "Duration(s)"])

        # Rows
        for it in export_data["iterations"]:
            writer.writerow([
                it["iteration_number"],
                it["status"],
                it["passed_criteria_count"],
                it["failed_criteria_count"],
                it["duration_seconds"],
            ])

        return {
            "format": "csv",
            "content": output.getvalue(),
        }
