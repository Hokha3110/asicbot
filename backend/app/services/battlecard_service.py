import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.battlecard import BattleCard
from app.models.solution import Solution
from app.services.llm_service import LLMService

BATTLECARD_PROMPT = """Bạn là Chuyên gia Chiến lược Presales & Competitive Intelligence.
Hãy tạo một bộ Solution Battle Card chi tiết và đầy đủ cho giải pháp an toàn thông tin dưới đây.

Phải trả về ĐÚNG ĐỊNH DẠNG JSON với cấu trúc:
{
  "solution_name": "Tên giải pháp",
  "vendor": "Tên Vendor",
  "category": "Nhóm giải pháp",
  "overview": "Tổng quan định vị giải pháp trong 2-3 câu",
  "why_customer_needs": "Lý do cấp thiết khách hàng phải mua ngay giải pháp này",
  "pain_points": [
    "Nỗi đau 1 của khách hàng",
    "Nỗi đau 2 của khách hàng",
    "Nỗi đau 3 của khách hàng"
  ],
  "talking_points": [
    "Luận điểm thuyết phục 1",
    "Luận điểm thuyết phục 2",
    "Luận điểm thuyết phục 3"
  ],
  "technical_advantages": [
    "Ưu thế kỹ thuật vượt trội 1 so với đối thủ",
    "Ưu thế kỹ thuật vượt trội 2",
    "Ưu thế kỹ thuật vượt trội 3"
  ],
  "common_objections": [
    {
      "objection": "Khách chê giá đắt hoặc chưa có ngân sách",
      "answer": "Cách Presales trả lời thuyết phục và giải quyết"
    },
    {
      "objection": "Khách đã có tường lửa / EDR / SIEM của hãng khác rồi",
      "answer": "Cách Presales giải thích tính năng bổ trợ độc nhất"
    },
    {
      "objection": "Khách lo ngại triển khai phức tạp, thiếu nhân sự vận hành",
      "answer": "Cách Presales trả lời về mức độ tự động hóa và hỗ trợ"
    }
  ],
  "target_buyer_personas": [
    "CISO / Head of Information Security",
    "SOC Lead / Security Operations Manager",
    "IT Director / Compliance Officer"
  ]
}
"""

class BattleCardService:
    @staticmethod
    async def generate_battlecard(
        solution_name: str,
        db: Session,
        vendor: Optional[str] = None,
        category: Optional[str] = None,
        llm_provider: Optional[str] = None,
        custom_openai_key: Optional[str] = None
    ) -> BattleCard:
        # Check if already exists in DB
        existing = db.query(BattleCard).filter(BattleCard.solution_name.ilike(f"%{solution_name}%")).first()
        if existing:
            return existing

        # Fetch solution details from DB if available
        sol = db.query(Solution).filter(Solution.name.ilike(f"%{solution_name}%")).first()
        ctx = f"Tên giải pháp: {solution_name}\n"
        if sol:
            ctx += f"Vendor: {sol.vendor}\nCategory: {sol.category}\nProblem: {sol.problem}\nFeatures: {', '.join(sol.features or [])}\nUse cases: {', '.join(sol.use_case or [])}\nCompetitors: {', '.join(sol.competitor or [])}"
        else:
            ctx += f"Vendor: {vendor or 'Security Vendor'}\nCategory: {category or 'Cybersecurity'}"

        prompt = f"{BATTLECARD_PROMPT}\n\nThông tin giải pháp:\n{ctx}\n\nHãy trả về JSON hợp lệ."
        
        response_text = await LLMService.generate_response(
            prompt=prompt,
            system_prompt="Bạn là trợ lý Presales JSON Generator. Chỉ trả về JSON hợp lệ.",
            llm_provider=llm_provider,
            custom_openai_key=custom_openai_key
        )

        try:
            # Clean markdown code blocks if any
            clean_json = response_text.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
            data = json.loads(clean_json)
        except Exception:
            # Fallback robust data
            data = {
                "solution_name": solution_name,
                "vendor": vendor or (sol.vendor if sol else "Security Vendor"),
                "category": category or (sol.category if sol else "Cybersecurity"),
                "overview": f"Giải pháp {solution_name} hàng đầu giúp doanh nghiệp nâng cao năng lực an toàn thông tin và chủ động ứng phó rủi ro.",
                "why_customer_needs": "Doanh nghiệp đối mặt với các cuộc tấn công ngày càng tinh vi và quy định tuân thủ pháp lý gắt gao.",
                "pain_points": [
                    "Thiếu khả năng hiển thị và kiểm soát bề mặt rủi ro.",
                    "Đội ngũ bảo mật quá tải cảnh báo và thiếu nhân lực chuyên sâu.",
                    "Nguy cơ bị phạt nặng và mất uy tín khi xảy ra sự cố rò rỉ dữ liệu."
                ],
                "talking_points": [
                    f"Giải pháp {solution_name} tối ưu hóa thời gian phát hiện và xử lý sự cố.",
                    "Tự động hóa quy trình vận hành giúp giảm 60% gánh nặng cho kỹ sư an ninh.",
                    "Chứng minh hiệu quả đầu tư bảo mật (Security ROI) rõ ràng cho Ban Giám Đốc."
                ],
                "technical_advantages": [
                    "Kiến trúc Cloud-native / Hybrid linh hoạt, triển khai nhanh trong vài giờ.",
                    "Tích hợp API sâu rộng với hệ sinh thái Firewall, EDR, SIEM hiện hữu.",
                    "Sử dụng AI/ML nhận diện mối đe dọa với độ chính xác cao, giảm thiểu False Positive."
                ],
                "common_objections": [
                    {
                        "objection": "Chúng tôi chưa có ngân sách cho giải pháp này trong năm nay.",
                        "answer": "Chúng tôi có chính sách PoC thử nghiệm miễn phí và các gói tài chính linh hoạt theo OPEX, giúp doanh nghiệp chứng minh ngay giá trị trước khi nghiệm thu."
                    },
                    {
                        "objection": "Hệ thống của chúng tôi đã có giải pháp bảo mật từ hãng lớn khác rồi.",
                        "answer": f"{solution_name} được thiết kế theo kiến trúc mở, không thay thế mà đóng vai trò tăng cường và tối ưu hóa năng lực cho các thiết bị hiện có."
                    }
                ],
                "target_buyer_personas": ["CISO", "Head of Security", "IT Director", "SOC Manager"]
            }

        new_bc = BattleCard(
            solution_id=sol.id if sol else None,
            solution_name=data.get("solution_name", solution_name),
            vendor=data.get("vendor", vendor or "Vendor"),
            category=data.get("category", category or "Category"),
            overview=data.get("overview", ""),
            why_customer_needs=data.get("why_customer_needs", ""),
            pain_points=data.get("pain_points", []),
            talking_points=data.get("talking_points", []),
            technical_advantages=data.get("technical_advantages", []),
            common_objections=data.get("common_objections", []),
            target_buyer_personas=data.get("target_buyer_personas", [])
        )
        db.add(new_bc)
        db.commit()
        db.refresh(new_bc)
        return new_bc
