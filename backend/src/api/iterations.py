"""Iterations API routes.

Handles iteration and conversation retrieval.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.conversation import Conversation, ConversationORM
from ..models.iteration import Iteration, IterationORM, IterationResponse
from ..storage.db import get_session

router = APIRouter()


@router.get("/iterations/{iteration_id}", response_model=IterationResponse)
async def get_iteration(
    iteration_id: UUID,
    db: Session = Depends(get_session),
) -> IterationResponse:
    """Get detailed iteration information.

    Args:
        iteration_id: Iteration UUID
        db: Database session

    Returns:
        Iteration details with evaluation results

    Raises:
        HTTPException: If iteration not found
    """
    iteration = (
        db.query(IterationORM).filter(IterationORM.id == str(iteration_id)).first()
    )

    if not iteration:
        raise HTTPException(
            status_code=404, detail=f"Iteration {iteration_id} not found"
        )

    return IterationResponse.model_validate(iteration)


@router.get("/iterations/{iteration_id}/conversations", response_model=list[Conversation])
async def get_iteration_conversations(
    iteration_id: UUID,
    db: Session = Depends(get_session),
) -> list[Conversation]:
    """Get all conversations for an iteration.

    Args:
        iteration_id: Iteration UUID
        db: Database session

    Returns:
        List of conversations

    Raises:
        HTTPException: If iteration not found
    """
    iteration = (
        db.query(IterationORM).filter(IterationORM.id == str(iteration_id)).first()
    )

    if not iteration:
        raise HTTPException(
            status_code=404, detail=f"Iteration {iteration_id} not found"
        )

    conversations = iteration.conversations

    return [Conversation.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_session),
) -> Conversation:
    """Get a single conversation with all turns.

    Args:
        conversation_id: Conversation UUID
        db: Database session

    Returns:
        Conversation details

    Raises:
        HTTPException: If conversation not found
    """
    conversation = (
        db.query(ConversationORM)
        .filter(ConversationORM.id == str(conversation_id))
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404, detail=f"Conversation {conversation_id} not found"
        )

    return Conversation.model_validate(conversation)
