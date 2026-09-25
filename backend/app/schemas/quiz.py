import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class QuizQuestionResponse(BaseModel):
    id: int
    solution_name: Optional[str] = None
    category: str
    question_text: str
    options: List[str]
    correct_option_index: int
    explanation: str
    difficulty: str
    is_daily_challenge: bool

    class Config:
        from_attributes = True

class QuizAnswerSubmit(BaseModel):
    question_id: int
    selected_option_index: int

class QuizSubmitRequest(BaseModel):
    answers: List[QuizAnswerSubmit]
    time_spent_seconds: int = 0

class QuizResultResponse(BaseModel):
    total_questions: int
    correct_answers: int
    score_percentage: int
    time_spent_seconds: int
    detailed_feedback: List[Dict[str, Any]]
    feedback_message: str

class QuizHistoryResponse(BaseModel):
    id: int
    username: str
    total_questions: int
    correct_answers: int
    score_percentage: int
    time_spent_seconds: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
