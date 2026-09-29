import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.vector_service import vector_service
from app.services.llm_service import LLMService
from app.models.solution import Solution
from app.schemas.chat import ChatResponse, SourceReference, DetectedSolution

# ─────────────────────────────────────────────────────────────────────────────
# Intent classifiers
# ─────────────────────────────────────────────────────────────────────────────

COMPARISON_SIGNALS = [
    "khác gì", "khác nhau", "so sánh", "compare", " vs ", "vs.", "khác biệt",
    "ưu điểm hơn", "tốt hơn", "kém hơn", "nên chọn", "hay là", "hay dùng",
    "phân biệt", "điểm khác", "điểm giống", "nào tốt hơn", "giữa", "thay thế nhau",
]

FOLLOWUP_SIGNALS = [
    "thêm", "chi tiết hơn", "giải thích thêm", "ví dụ", "cụ thể",
    "thế nào", "như thế nào", "ý nghĩa", "hiểu rõ", "nói rõ",
    "tiếp theo", "bước tiếp", "làm sao", "triển khai", "deploy",
    "tích hợp", "kết nối", "pricing", "giá cả", "poc", "thử nghiệm", "demo",
    "bao nhiêu", "license", "giấy phép",
]

QUESTION_SIGNALS = [
    "là gì", "định nghĩa", "khái niệm", "explain", "what is",
    "giới thiệu về", "tổng quan về", "overview",
]


def _classify_intent(message: str, history: List[Dict[str, Any]]) -> str:
    """Returns: 'comparison' | 'followup' | 'question' | 'presales_pitch'"""
    lower = message.lower()

    if any(sig in lower for sig in COMPARISON_SIGNALS):
        return "comparison"

    if any(sig in lower for sig in FOLLOWUP_SIGNALS) and history:
        return "followup"

    if any(sig in lower for sig in QUESTION_SIGNALS):
        return "question"

    return "presales_pitch"


# ─────────────────────────────────────────────────────────────────────────────
# System prompts per intent
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_PRESALES_PITCH = """Bạn là Kali0t, Senior Security Presales Architect AI.
Nhiệm vụ của bạn là tư vấn giải pháp an toàn thông tin chuyên nghiệp cho đội ngũ Presales và khách hàng doanh nghiệp.

QUY TẮC BẮT BUỘC:
- Chỉ sử dụng thông tin có trong context tài liệu hoặc thông tin chắc chắn từ câu hỏi.
- Không tự bịa tên sản phẩm, tính năng, số liệu, trang tài liệu hoặc đối thủ.
- Nếu context không đủ hoặc câu hỏi mơ hồ, ghi rõ chưa đủ dữ liệu và hỏi tối đa 3 câu làm rõ.
- Source reference chỉ được trích dẫn các tài liệu và trang thực sự xuất hiện trong context.

Mọi câu trả lời PHẢI tuân theo đúng định dạng Markdown 8 mục sau:

## Solution
[Tên giải pháp chính xác và Vendor]

## Category
[SOC / DLP / PAM / BAS / DSPM / DevSecOps / Identity...]

## Problem solved
[Giải quyết vấn đề và nỗi đau gì của khách hàng]

## Key capability
- [Tính năng cốt lõi 1]
- [Tính năng cốt lõi 2]
- [Tính năng cốt lõi 3]

## Use case
- [Use case điển hình 1]
- [Use case điển hình 2]

## Customer discovery questions
1. [Câu hỏi khai thác nhu cầu]
2. [Câu hỏi khai thác hiện trạng kỹ thuật]
3. [Câu hỏi về timeline và tiêu chí lựa chọn]

## Competitor / Alternative
- [Đối thủ 1]
- [Đối thủ 2]

## Source reference
Document: [Tên tài liệu]
Page: [Trang]
"""

SYSTEM_PROMPT_COMPARISON = """Bạn là Kali0t, Senior Security Presales Architect AI chuyên về so sánh giải pháp.

QUY TẮC:
- Trả lời TẬP TRUNG vào CÂU HỎI SO SÁNH cụ thể. KHÔNG dùng format 8 mục chuẩn.
- Chỉ dựa trên context tài liệu được cung cấp và lịch sử hội thoại.
- Nếu không đủ thông tin về một sản phẩm, nói rõ.
- Dùng bảng Markdown để so sánh rõ ràng.

Cấu trúc trả lời:

## So sánh: [Sản phẩm A] vs [Sản phẩm B]

### Điểm giống nhau
- ...

### Điểm khác biệt chính
| Tiêu chí | [Sản phẩm A] | [Sản phẩm B] |
|---|---|---|
| Mục đích chính | ... | ... |
| Cách hoạt động | ... | ... |
| Đối tượng dùng | ... | ... |

### Khi nào chọn [Sản phẩm A]?
- ...

### Khi nào chọn [Sản phẩm B]?
- ...

### Gợi ý tư vấn cho Presales
- ...
"""

SYSTEM_PROMPT_FOLLOWUP = """Bạn là Kali0t, Senior Security Presales Architect AI.
Đây là câu hỏi TIẾP NỐI cuộc trò chuyện. Hãy trả lời TẬP TRUNG, NGẮN GỌN và ĐI VÀO CHI TIẾT mà người dùng yêu cầu.
KHÔNG lặp lại toàn bộ thông tin đã trình bày trước đó.
Chỉ sử dụng thông tin từ context tài liệu và lịch sử hội thoại.
Trả lời bằng Markdown có cấu trúc rõ ràng."""

SYSTEM_PROMPT_QUESTION = """Bạn là Kali0t, Senior Security Presales Architect AI.
Hãy GIẢI THÍCH RÕ RÀNG khái niệm hoặc câu hỏi được đặt ra.
Sử dụng ngôn ngữ dễ hiểu, có thể dùng ví dụ thực tế trong ngành bảo mật.
Chỉ dựa trên thông tin từ context tài liệu được cung cấp.
Trả lời bằng Markdown có cấu trúc."""


def _select_system_prompt(intent: str) -> str:
    return {
        "comparison": SYSTEM_PROMPT_COMPARISON,
        "followup": SYSTEM_PROMPT_FOLLOWUP,
        "question": SYSTEM_PROMPT_QUESTION,
        "presales_pitch": SYSTEM_PROMPT_PRESALES_PITCH,
    }.get(intent, SYSTEM_PROMPT_PRESALES_PITCH)


def _build_prompt(intent: str, message: str, combined_context: str, history_text: str) -> str:
    base = f"""Thông tin trích xuất từ tài liệu giải pháp:

{combined_context}
{history_text}"""

    if intent == "comparison":
        return base + f"""

YÊU CẦU SO SÁNH TỪ PRESALES:
"{message}"

Hãy so sánh chi tiết và chính xác dựa trên context tài liệu trên. Nếu không có đủ dữ liệu cho một sản phẩm, hãy nói rõ."""

    elif intent == "followup":
        return base + f"""

CÂU HỎI TIẾP THEO:
"{message}"

Hãy trả lời tập trung vào đúng điều được hỏi, không lặp lại thông tin cũ."""

    elif intent == "question":
        return base + f"""

CÂU HỎI:
"{message}"

Hãy giải thích rõ ràng và súc tích."""

    else:  # presales_pitch
        return base + f"""

YÊU CẦU TƯ VẤN TỪ PRESALES / KHÁCH HÀNG:
"{message}"

Hãy trả lời chi tiết, chuẩn xác theo đúng 8 mục định dạng Presales. Nếu không đủ bằng chứng, nói rõ chưa đủ dữ liệu thay vì suy đoán."""


# ─────────────────────────────────────────────────────────────────────────────
# RAGService
# ─────────────────────────────────────────────────────────────────────────────

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

        # ── 0. Classify intent ─────────────────────────────────────────────
        intent = _classify_intent(message, history or [])

        # ── 1. Build augmented query for comparison questions ──────────────
        # Pull recent assistant text so both products get retrieved
        search_query = message
        if intent == "comparison" and history:
            last_assistant = next(
                (h["content"] for h in reversed(history) if h.get("role") == "assistant"),
                ""
            )
            search_query = f"{message} {last_assistant[:400]}"

        # ── 2. Retrieve relevant chunks from Vector DB ─────────────────────
        filter_dict = None
        if selected_documents and len(selected_documents) > 0:
            if len(selected_documents) == 1:
                filter_dict = {"document_name": selected_documents[0]}
            else:
                filter_dict = {"document_name": {"$in": selected_documents}}

        top_k = 8 if intent == "comparison" else 5
        retrieved_chunks = vector_service.query_similar(search_query, top_k=top_k, filter_dict=filter_dict)

        # ── 3. Extract sources ─────────────────────────────────────────────
        sources: List[SourceReference] = []
        context_texts = []
        for chunk in retrieved_chunks:
            meta = chunk.get("metadata", {})
            doc_name = meta.get("document_name", "Security Solution Document")
            page_num = meta.get("page_number", 1)
            vendor = meta.get("vendor", "")
            cat = meta.get("solution_category", "")

            context_texts.append(
                f"[Tài liệu: {doc_name} | Trang: {page_num} | Vendor: {vendor} | Nhóm: {cat}]\n{chunk['text']}"
            )

            if not any(s.document_name == doc_name and s.page_number == page_num for s in sources):
                sources.append(SourceReference(
                    document_name=doc_name,
                    page_number=page_num,
                    snippet=chunk["text"][:200] + "...",
                    vendor=vendor,
                    category=cat
                ))

        # ── 4. Detect known solutions ──────────────────────────────────────
        detected_solutions: List[DetectedSolution] = []
        all_solutions = db.query(Solution).all()

        history_text_for_match = " ".join(
            h.get("content", "") for h in (history or [])[-4:]
        )
        lower_query_and_ctx = (
            message + " " + history_text_for_match + " " +
            " ".join([c["text"] for c in retrieved_chunks])
        ).lower()

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

        # ── 5. Build Prompt ────────────────────────────────────────────────
        combined_context = "\n\n---\n\n".join(context_texts) if context_texts else "Dữ liệu tri thức giải pháp có sẵn."

        history_window = 8 if intent in ("followup", "comparison") else 4
        history_text = ""
        if history:
            history_text = "\n\nLỊCH SỬ TRAO ĐỔI GẦN ĐÂY:\n" + "\n".join(
                f"[{item.get('role', 'user').upper()}]: {item.get('content', '')}"
                for item in history[-history_window:]
            )

        system_prompt = _select_system_prompt(intent)
        prompt = _build_prompt(intent, message, combined_context, history_text)

        reply = await LLMService.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            custom_gemini_key=custom_gemini_key,
            custom_openai_key=custom_openai_key,
            custom_ollama_url=custom_ollama_url,
            intent_text=message
        )

        return ChatResponse(
            reply=reply,
            detected_solutions=detected_solutions,
            sources=sources,
            mode_applied=None
        )
