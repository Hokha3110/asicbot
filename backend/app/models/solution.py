import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.database import Base

class Solution(Base):
    __tablename__ = "solutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, index=True, nullable=False)
    vendor = Column(String(200), index=True, nullable=False)
    category = Column(String(100), index=True, nullable=False) # "SOC", "DLP", "PAM", "BAS", "DSPM", "DevSecOps"...
    problem = Column(Text, nullable=False) # Problem solved
    description = Column(Text, nullable=False)
    features = Column(JSON, default=list) # List of key capabilities
    use_case = Column(JSON, default=list) # List of use cases
    competitor = Column(JSON, default=list) # List of competitors / alternatives
    keywords = Column(JSON, default=list) # List of search keywords e.g. ["BAS", "MITRE ATT&CK", "CTEM"]
    discovery_questions = Column(JSON, default=list) # Presales customer discovery questions
    documents = Column(JSON, default=list) # Referenced documents & pages
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
