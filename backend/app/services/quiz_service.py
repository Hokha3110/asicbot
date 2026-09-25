import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.quiz import QuizQuestion, QuizHistory
from app.models.solution import Solution
from app.schemas.quiz import QuizSubmitRequest, QuizResultResponse

class QuizService:
    @staticmethod
    def get_daily_questions(db: Session, limit: int = 5) -> List[QuizQuestion]:
        """
        Retrieves active quiz questions for presales practice / daily challenge.
        """
        questions = db.query(QuizQuestion).filter(QuizQuestion.is_daily_challenge == True).limit(limit).all()
        if len(questions) < limit:
            # Also get regular questions
            extra = db.query(QuizQuestion).filter(QuizQuestion.is_daily_challenge == False).limit(limit - len(questions)).all()
            questions.extend(extra)
        return questions

    @staticmethod
    def submit_and_evaluate(db: Session, username: str, submission: QuizSubmitRequest) -> QuizResultResponse:
        """
        Evaluates submitted quiz answers, records quiz history, and returns detailed explanations.
        """
        total_questions = len(submission.answers)
        correct_count = 0
        detailed_feedback = []

        for item in submission.answers:
            q = db.query(QuizQuestion).filter(QuizQuestion.id == item.question_id).first()
            if q:
                is_correct = (item.selected_option_index == q.correct_option_index)
                if is_correct:
                    correct_count += 1
                
                selected_text = q.options[item.selected_option_index] if 0 <= item.selected_option_index < len(q.options) else "Chưa chọn"
                correct_text = q.options[q.correct_option_index] if 0 <= q.correct_option_index < len(q.options) else ""

                detailed_feedback.append({
                    "question_id": q.id,
                    "question_text": q.question_text,
                    "solution_name": q.solution_name,
                    "selected_option_index": item.selected_option_index,
                    "selected_option_text": selected_text,
                    "correct_option_index": q.correct_option_index,
                    "correct_option_text": correct_text,
                    "is_correct": is_correct,
                    "explanation": q.explanation
                })

        score_pct = int((correct_count / total_questions * 100)) if total_questions > 0 else 0

        # Save history
        history_entry = QuizHistory(
            username=username,
            total_questions=total_questions,
            correct_answers=correct_count,
            score_percentage=score_pct,
            time_spent_seconds=submission.time_spent_seconds,
            details=detailed_feedback
        )
        db.add(history_entry)
        db.commit()

        # Generate presales badge/message
        if score_pct == 100:
            msg = "Xuất sắc! Bạn nắm vững 100% kiến thức giải pháp và sẵn sàng tư vấn CISO!"
        elif score_pct >= 80:
            msg = "Rất tốt! Bạn hiểu sâu sắc các giải pháp và kịch bản Presales."
        elif score_pct >= 60:
            msg = "Khá tốt! Hãy ôn lại một số tính năng và câu hỏi discovery để tự tin hơn."
        else:
            msg = "Cần cố gắng thêm! Hãy xem lại tài liệu Document Center và Battle Cards để nâng cao kiến thức."

        return QuizResultResponse(
            total_questions=total_questions,
            correct_answers=correct_count,
            score_percentage=score_pct,
            time_spent_seconds=submission.time_spent_seconds,
            detailed_feedback=detailed_feedback,
            feedback_message=msg
        )
