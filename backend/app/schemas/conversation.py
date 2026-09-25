import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationSummary(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class ConversationMessageCreate(BaseModel):
    role: str
    content: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    detected_solutions: List[Dict[str, Any]] = Field(default_factory=list)
    mode_applied: Optional[str] = None


class ConversationMessageResponse(ConversationMessageCreate):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ConversationResponse(ConversationSummary):
    messages: List[ConversationMessageResponse] = Field(default_factory=list)
