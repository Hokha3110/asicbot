from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.quiz import QuizQuestion, QuizHistory
from app.models.user import User
from app.schemas.quiz import QuizQuestionResponse, QuizSubmitRequest, QuizResultResponse, QuizHistoryResponse
from app.services.quiz_service import QuizService
from app.utils.security import require_current_user

router = APIRouter(prefix="/api/v1/academy", tags=["Security Academy"])

@router.get("/daily-challenge", response_model=List[QuizQuestionResponse])
def get_daily_challenge(db: Session = Depends(get_db)):
    """
    Returns 5 random/daily questions for presales practice.
    """
    questions = QuizService.get_daily_questions(db, limit=5)
    return questions

@router.get("/questions", response_model=List[QuizQuestionResponse])
def get_all_questions(db: Session = Depends(get_db)):
    return db.query(QuizQuestion).all()

@router.post("/submit", response_model=QuizResultResponse)
def submit_quiz(
    submission: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    username = current_user.username if current_user else "presales_engineer"
    result = QuizService.submit_and_evaluate(db, username, submission)
    return result

@router.get("/history", response_model=List[QuizHistoryResponse])
def get_quiz_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user)
):
    query = db.query(QuizHistory)
    if current_user and current_user.role != "admin":
        query = query.filter(QuizHistory.username == current_user.username)
    return query.order_by(QuizHistory.created_at.desc()).limit(20).all()
