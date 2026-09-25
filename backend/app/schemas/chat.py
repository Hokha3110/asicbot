from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str # "user", "assistant", "system"
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    selected_documents: Optional[List[str]] = None
    llm_provider: Optional[str] = None # "gemini", "openai", "ollama", "mock"
    custom_gemini_key: Optional[str] = None
    custom_openai_key: Optional[str] = None
    custom_ollama_url: Optional[str] = None

class PresalesModeRequest(BaseModel):
    mode: str # "technical", "customer", "sales_pitch", "email_draft", "create_slide"
    solution_name: Optional[str] = None
    context_text: str
    custom_requirements: Optional[str] = None
    llm_provider: Optional[str] = None
    custom_gemini_key: Optional[str] = None
    custom_openai_key: Optional[str] = None

class SourceReference(BaseModel):
    document_name: str
    page_number: int
    snippet: str
    vendor: Optional[str] = None
    category: Optional[str] = None

class DetectedSolution(BaseModel):
    id: Optional[int] = None
    name: str
    vendor: str
    category: str
    summary: str

class ChatResponse(BaseModel):
    reply: str
    detected_solutions: List[DetectedSolution] = []
    sources: List[SourceReference] = []
    mode_applied: Optional[str] = None
