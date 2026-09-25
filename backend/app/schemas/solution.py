import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SolutionBase(BaseModel):
    name: str
    vendor: str
    category: str
    problem: str
    description: str
    features: List[str] = []
    use_case: List[str] = []
    competitor: List[str] = []
    keywords: List[str] = []
    discovery_questions: List[str] = []
    documents: List[Dict[str, Any]] = []

class SolutionCreate(SolutionBase):
    pass

class SolutionUpdate(BaseModel):
    name: Optional[str] = None
    vendor: Optional[str] = None
    category: Optional[str] = None
    problem: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    use_case: Optional[List[str]] = None
    competitor: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    discovery_questions: Optional[List[str]] = None
    documents: Optional[List[Dict[str, Any]]] = None

class SolutionResponse(SolutionBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class SmartSearchQuery(BaseModel):
    query: str
    category: Optional[str] = None
    top_k: int = 5
