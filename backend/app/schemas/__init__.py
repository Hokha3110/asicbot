from app.schemas.auth import UserLogin, UserCreate, UserResponse, Token
from app.schemas.document import DocumentMetadata, DocumentResponse, DocumentUploadResponse
from app.schemas.solution import SolutionBase, SolutionCreate, SolutionUpdate, SolutionResponse, SmartSearchQuery
from app.schemas.battlecard import BattleCardBase, BattleCardCreate, BattleCardResponse, BattleCardGenerateRequest
from app.schemas.quiz import QuizQuestionResponse, QuizSubmitRequest, QuizResultResponse, QuizHistoryResponse
from app.schemas.chat import ChatRequest, ChatResponse, PresalesModeRequest, SourceReference, DetectedSolution

__all__ = [
    "UserLogin", "UserCreate", "UserResponse", "Token",
    "DocumentMetadata", "DocumentResponse", "DocumentUploadResponse",
    "SolutionBase", "SolutionCreate", "SolutionUpdate", "SolutionResponse", "SmartSearchQuery",
    "BattleCardBase", "BattleCardCreate", "BattleCardResponse", "BattleCardGenerateRequest",
    "QuizQuestionResponse", "QuizSubmitRequest", "QuizResultResponse", "QuizHistoryResponse",
    "ChatRequest", "ChatResponse", "PresalesModeRequest", "SourceReference", "DetectedSolution"
]
