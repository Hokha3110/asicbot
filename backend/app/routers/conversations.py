from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation, ConversationMessage
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationMessageCreate,
    ConversationResponse,
    ConversationSummary,
)
from app.utils.security import require_current_user

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversation History"])


def _get_owned_conversation(conversation_id: int, user: User, db: Session) -> Conversation:
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuộc trò chuyện")
    return conversation


@router.get("", response_model=List[ConversationSummary])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


@router.post("", response_model=ConversationSummary, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    conversation = Conversation(
        user_id=current_user.id,
        title=(payload.title or "Cuộc trò chuyện mới").strip()[:255],
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    conversation = _get_owned_conversation(conversation_id, current_user, db)
    conversation.messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conversation.id)
        .order_by(ConversationMessage.created_at.asc(), ConversationMessage.id.asc())
        .all()
    )
    return conversation


@router.post("/{conversation_id}/messages", response_model=ConversationResponse)
def add_message(
    conversation_id: int,
    payload: ConversationMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    conversation = _get_owned_conversation(conversation_id, current_user, db)
    message = ConversationMessage(
        conversation_id=conversation.id,
        role=payload.role,
        content=payload.content,
        sources=payload.sources,
        detected_solutions=payload.detected_solutions,
        mode_applied=payload.mode_applied,
    )
    db.add(message)
    conversation.updated_at = __import__("datetime").datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    conversation.messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.conversation_id == conversation.id)
        .order_by(ConversationMessage.created_at.asc(), ConversationMessage.id.asc())
        .all()
    )
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    conversation = _get_owned_conversation(conversation_id, current_user, db)
    db.delete(conversation)
    db.commit()
