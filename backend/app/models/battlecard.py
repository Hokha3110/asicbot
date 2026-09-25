import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from app.database import Base

class BattleCard(Base):
    __tablename__ = "battle_cards"

    id = Column(Integer, primary_key=True, index=True)
    solution_id = Column(Integer, ForeignKey("solutions.id", ondelete="CASCADE"), nullable=True)
    solution_name = Column(String(200), index=True, nullable=False)
    vendor = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    overview = Column(Text, nullable=False)
    why_customer_needs = Column(Text, nullable=False)
    pain_points = Column(JSON, default=list) # List of customer pain points
    talking_points = Column(JSON, default=list) # List of presales talking points / pitch
    technical_advantages = Column(JSON, default=list) # List of technical pros over competition
    common_objections = Column(JSON, default=list) # [{ "objection": "...", "answer": "..." }]
    target_buyer_personas = Column(JSON, default=list) # ["CISO", "SOC Lead", "Compliance Officer"]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
