import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ObjectionHandling(BaseModel):
    objection: str
    answer: str

class BattleCardBase(BaseModel):
    solution_id: Optional[int] = None
    solution_name: str
    vendor: str
    category: str
    overview: str
    why_customer_needs: str
    pain_points: List[str] = []
    talking_points: List[str] = []
    technical_advantages: List[str] = []
    common_objections: List[ObjectionHandling] = []
    target_buyer_personas: List[str] = []

class BattleCardCreate(BattleCardBase):
    pass

class BattleCardGenerateRequest(BaseModel):
    solution_name: str
    vendor: Optional[str] = None
    category: Optional[str] = None

class BattleCardResponse(BattleCardBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
