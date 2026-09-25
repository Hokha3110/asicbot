from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, PresalesModeRequest
from app.services.rag_service import RAGService
from app.services.presales_modes import PresalesModeService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/chat", tags=["AI Presales Assistant"])

@router.post("", response_model=ChatResponse)
async def chat_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Main Presales Chat Endpoint enforcing standard Presales 8-section response format.
    """
    history_dicts = [h.dict() for h in request.history] if request.history else []
    
    response = await RAGService.chat(
        message=request.message,
        db=db,
        history=history_dicts,
        llm_provider=request.llm_provider,
        custom_gemini_key=request.custom_gemini_key,
        custom_openai_key=request.custom_openai_key,
        custom_ollama_url=request.custom_ollama_url,
        selected_documents=request.selected_documents
    )
    return response

@router.post("/mode-transform")
async def transform_presales_mode(
    request: PresalesModeRequest
):
    """
    Transforms solution context into Technical, Customer, Sales Pitch, Email Draft, or Slide Outline.
    """
    result_text = await PresalesModeService.transform(
        mode=request.mode,
        context_text=request.context_text,
        solution_name=request.solution_name,
        custom_requirements=request.custom_requirements,
        llm_provider=request.llm_provider,
        custom_gemini_key=request.custom_gemini_key,
        custom_openai_key=request.custom_openai_key
    )
    return {
        "mode": request.mode,
        "solution_name": request.solution_name,
        "content": result_text
    }
