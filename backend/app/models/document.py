import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False) # "pdf", "docx", "pptx"
    vendor = Column(String(100), default="General Security")
    solution_category = Column(String(100), default="General")
    page_count = Column(Integer, default=1)
    chunk_count = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    status = Column(String(50), default="indexed") # "processing", "indexed", "failed"
    doc_metadata = Column(JSON, default=dict)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
