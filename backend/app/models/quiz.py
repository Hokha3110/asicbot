import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from app.database import Base

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    solution_name = Column(String(200), nullable=True)
    category = Column(String(100), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False) # ["SIEM", "BAS", "DLP", "PAM"]
    correct_option_index = Column(Integer, nullable=False) # 0, 1, 2, 3
    explanation = Column(Text, nullable=False)
    difficulty = Column(String(50), default="Medium") # Easy, Medium, Hard
    is_daily_challenge = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class QuizHistory(Base):
    __tablename__ = "quiz_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    username = Column(String(100), nullable=False)
    total_questions = Column(Integer, default=5)
    correct_answers = Column(Integer, default=0)
    score_percentage = Column(Integer, default=0)
    time_spent_seconds = Column(Integer, default=0)
    details = Column(JSON, default=list) # [{ question_id, user_choice, is_correct }]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
