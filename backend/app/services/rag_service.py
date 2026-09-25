import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.vector_service import vector_service
from app.services.llm_service import LLMService
from app.models.solution import Solution
from app.schemas.chat import ChatResponse, SourceReference, DetectedSolution

STANDARD_PRESALES_SYSTEM_PROMPT = """Bạn là Senior Security Presales Architect AI tại Security Solution Copilot.
Nhiệm vụ của bạn là tư vấn giải pháp an toàn thông tin chuyên nghiệp cho đội ngũ Presales và khách hàng doanh nghiệp.

QUY TẮC BẮT BUỘC:
Mọi câu trả lời của bạn PHẢI tuân theo đúng định dạng Markdown chính xác sau:

## Solution
[Tên giải pháp chính xác và Vendor]

## Category
[Phân loại: SOC / DLP / PAM / BAS / DSPM / DevSecOps / Identity...]

## Problem solved
[Giải quyết vấn đề và nỗi đau gì của khách hàng một cách sắc bén]

## Key capability
- [Tính năng và năng lực kỹ thuật cốt lõi 1]
- [Tính năng và năng lực kỹ thuật cốt lõi 2]
- [Tính năng và năng lực kỹ thuật cốt lõi 3]

## Use case
- [Tình huống và use case khách hàng điển hình 1]
- [Tình huống và use case khách hàng điển hình 2]

## Customer discovery questions
1. [Câu hỏi khai thác nhu cầu và ngân sách 1]
2. [Câu hỏi khai thác hiện trạng kỹ thuật 2]
3. [Câu hỏi về timeline và tiêu chí lựa chọn 3]

## Competitor / Alternative
- [Đối thủ cạnh tranh hoặc phương án thay thế 1]
- [Đối thủ cạnh tranh hoặc phương án thay thế 2]

## Source reference
Document: [Tên tài liệu]
Page: [Trang tài liệu liên quan]
"""

class RAGService:
    @staticmethod
    async def chat(
        message: str,
        db: Session,
        history: Optional[List[Dict[str, Any]]] = None,
        llm_provider: Optional[str] = None,
        custom_gemini_key: Optional[str] = None,
        custom_openai_key: Optional[str] = None,
        custom_ollama_url: Optional[str] = None,
        selected_documents: Optional[List[str]] = None
    ) -> ChatResponse:
        # 1. Retrieve relevant chunks from Vector DB
        filter_dict = None
        if selected_documents and len(selected_documents) > 0:
            if len(selected_documents) == 1:
                filter_dict = {"document_name": selected_documents[0]}
            else:
                filter_dict = {"document_name": {"$in": selected_documents}}

        retrieved_chunks = vector_service.query_similar(message, top_k=5, filter_dict=filter_dict)
        
        # 2. Extract sources
        sources: List[SourceReference] = []
        context_texts = []
        for chunk in retrieved_chunks:
            meta = chunk.get("metadata", {})
            doc_name = meta.get("document_name", "Security Solution Document")
            page_num = meta.get("page_number", 1)
            vendor = meta.get("vendor", "")
            cat = meta.get("solution_category", "")
            
            context_texts.append(f"[Tài liệu: {doc_name} | Trang: {page_num} | Vendor: {vendor} | Nhóm: {cat}]\n{chunk['text']}")
            
            # Avoid duplicate source references
            if not any(s.document_name == doc_name and s.page_number == page_num for s in sources):
                sources.append(SourceReference(
                    document_name=doc_name,
                    page_number=page_num,
                    snippet=chunk['text'][:200] + "...",
                    vendor=vendor,
                    category=cat
                ))

        # 3. Detect known solutions in DB based on query and retrieved content
        detected_solutions: List[DetectedSolution] = []
        all_solutions = db.query(Solution).all()
        
        lower_query_and_ctx = (message + " " + " ".join([c["text"] for c in retrieved_chunks])).lower()
        
        for sol in all_solutions:
            sol_keywords = [k.lower() for k in (sol.keywords or [])] + [sol.name.lower(), sol.vendor.lower()]
            if any(k in lower_query_and_ctx for k in sol_keywords if len(k) > 2):
                if not any(d.name == sol.name for d in detected_solutions):
                    detected_solutions.append(DetectedSolution(
                        id=sol.id,
                        name=sol.name,
                        vendor=sol.vendor,
                        category=sol.category,
                        summary=sol.problem[:150] + "..."
                    ))

        # 4. Build Prompt for LLM
        combined_context = "\n\n---\n\n".join(context_texts) if context_texts else "Dữ liệu tri thức giải pháp có sẵn."
        
        prompt = f"""Bạn là Kali0t, trợ lý Senior Security Presales Architect.

    Dưới đây là thông tin trích xuất từ tài liệu giải pháp của chúng ta:

{combined_context}

YÊU CẦU CỦA PRESALES / KHÁCH HÀNG:
"{message}"

Hãy trả lời chi tiết, chuẩn xác và bắt buộc tuân theo đúng 8 mục định dạng Presales."""

        reply = await LLMService.generate_response(
            prompt=prompt,
            system_prompt=STANDARD_PRESALES_SYSTEM_PROMPT,
            llm_provider=llm_provider,
            custom_gemini_key=custom_gemini_key,
            custom_openai_key=custom_openai_key,
            custom_ollama_url=custom_ollama_url
        )

        return ChatResponse(
            reply=reply,
            detected_solutions=detected_solutions,
            sources=sources,
            mode_applied=None
        )
