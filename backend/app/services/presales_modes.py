from typing import Optional
from app.services.llm_service import LLMService

class PresalesModeService:
    @staticmethod
    async def transform(
        mode: str,
        context_text: str,
        solution_name: Optional[str] = None,
        custom_requirements: Optional[str] = None,
        llm_provider: Optional[str] = None,
        custom_gemini_key: Optional[str] = None,
        custom_openai_key: Optional[str] = None
    ) -> str:
        """
        Transforms presales context into specific Presales Artifacts (Technical, Customer, Sales Pitch, Email, Slides).
        """
        target_solution = solution_name or "Giải pháp bảo mật"
        extra_req = f"\nYêu cầu bổ sung: {custom_requirements}" if custom_requirements else ""

        if mode == "technical":
            system_prompt = (
                "Bạn là Principal Security Architect. Hãy giải thích chi tiết về mặt KỸ THUẬT cho Technical Lead / SOC Manager / DevOps. "
                "Bao gồm: Kiến trúc triển khai (Agent vs Agentless, On-prem/Cloud/Hybrid), Luồng xử lý dữ liệu (Data flow & Protocols), "
                "Cổng kết nối (Network Ports & Traffic), Khả năng tích hợp API/SIEM/SOAR/ITSM, Yêu cầu tài nguyên phần cứng, và Khả năng chịu tải HA."
            )
            prompt = f"Giải thích kỹ thuật chuyên sâu cho giải pháp [{target_solution}] dựa trên nội dung sau:{extra_req}\n\n{context_text}"

        elif mode == "customer":
            system_prompt = (
                "Bạn là Senior Cybersecurity Consultant. Hãy giải thích giải pháp bằng NGÔN NGỮ KINH DOANH DỄ HIỂU (Customer-friendly) cho C-Level (CEO, CFO, CISO) "
                "hoặc khách hàng không chuyên kỹ thuật. Tránh dùng từ ngữ kỹ thuật phức tạp khó hiểu. "
                "Hãy dùng ví dụ thực tế hoặc hình ảnh ẩn dụ (metaphor), tập trung vào giá trị bảo vệ tài sản, ngăn chặn tổn thất uy tín và tiền bạc."
            )
            prompt = f"Chuyển đổi thông tin giải pháp [{target_solution}] thành ngôn ngữ dễ hiểu cho lãnh đạo doanh nghiệp:{extra_req}\n\n{context_text}"

        elif mode == "sales_pitch":
            system_prompt = (
                "Bạn là Top Performer Presales Director. Hãy tạo một bài SALES PITCH tư vấn khách hàng sắc bén, thuyết phục và lôi cuốn. "
                "Cấu trúc gồm: 1. Đánh trúng nỗi đau (Pain Point), 2. Thực trạng rủi ro nếu không hành động (Cost of Inaction), "
                "3. Sự khác biệt độc tôn của giải pháp (Unique Selling Proposition - USP), 4. Giá trị ROI & Tuân thủ pháp luật (Nghị định 13, ISO 27001), 5. Kêu gọi hành động (Call To Action - Đề xuất PoC)."
            )
            prompt = f"Tạo kịch bản Sales Pitch đỉnh cao cho giải pháp [{target_solution}]:{extra_req}\n\n{context_text}"

        elif mode == "email_draft":
            system_prompt = (
                "Bạn là Chuyên gia Presales chuyên nghiệp. Hãy soạn một EMAIL FOLLOW-UP chuẩn mực, lịch sự và trang trọng gửi cho khách hàng sau buổi họp tư vấn giải pháp. "
                "Bao gồm: Tiêu đề email cuốn hút; Lời cảm ơn; Tóm tắt 3 điểm chính đã thảo luận; Đề xuất lộ trình tiếp theo (Cung cấp tài liệu chi tiết, Lập kế hoạch PoC thử nghiệm 14 ngày miễn phí, Cuộc họp kỹ thuật tiếp theo); Chữ ký chuyên nghiệp."
            )
            prompt = f"Soạn email follow-up gửi khách hàng về giải pháp [{target_solution}]:{extra_req}\n\n{context_text}"

        elif mode == "create_slide":
            system_prompt = (
                "Bạn là Trưởng bộ phận Giải pháp Presales. Hãy tạo OUTLINE SLIDE THUYẾT TRÌNH (Presentation Slide Deck Outline) gồm 5-7 slide chuyên nghiệp. "
                "Mỗi slide bao gồm: [Slide X: Tiêu đề Slide], [Mục tiêu truyền tải], [Nội dung Bullet Points chính], [Gợi ý biểu đồ/Hình ảnh minh họa], [Ghi chú cho diễn giả (Speaker Notes)]."
            )
            prompt = f"Tạo dàn ý slide thuyết trình chuyên nghiệp cho giải pháp [{target_solution}]:{extra_req}\n\n{context_text}"

        else:
            system_prompt = "Bạn là trợ lý Presales An toàn thông tin chuyên nghiệp."
            prompt = f"Tư vấn giải pháp [{target_solution}]:\n\n{context_text}"

        return await LLMService.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            llm_provider=llm_provider,
            custom_gemini_key=custom_gemini_key,
            custom_openai_key=custom_openai_key
        )
