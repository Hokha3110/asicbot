import httpx
import json
from typing import List, Dict, Any, Optional
from app.config import settings

class LLMService:
    @staticmethod
    async def generate_response(
        prompt: str,
        system_prompt: Optional[str] = None,
        llm_provider: Optional[str] = None,
        custom_gemini_key: Optional[str] = None,
        custom_openai_key: Optional[str] = None,
        custom_ollama_url: Optional[str] = None,
        intent_text: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """
        Multi-provider LLM response generator (Google Gemini, OpenAI, Ollama, Smart Presales Mock).
        """
        provider = (llm_provider or settings.DEFAULT_LLM_PROVIDER).lower()
        gemini_key = custom_gemini_key or settings.GEMINI_API_KEY
        openai_key = custom_openai_key or settings.OPENAI_API_KEY
        ollama_url = custom_ollama_url or settings.OLLAMA_BASE_URL

        # 1. Try Google Gemini if selected or key exists
        if (provider == "gemini" or gemini_key) and gemini_key and not gemini_key.startswith("your_gemini"):
            try:
                model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
                if "gemini" not in model_name:
                    model_name = "gemini-2.5-flash"

                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                headers = {"Content-Type": "application/json"}
                
                # Check key format
                if gemini_key.startswith("AIzaSy"):
                    url += f"?key={gemini_key}"
                else:
                    headers["Authorization"] = f"Bearer {gemini_key}"
                    url += f"?key={gemini_key}" # Provide both for maximum compatibility
                
                contents = []
                if system_prompt:
                    contents.append({
                        "role": "user",
                        "parts": [{"text": f"VAI TRÒ PRESALES & ĐỊNH DẠNG BẮT BUỘC:\n{system_prompt}"}]
                    })
                    contents.append({
                        "role": "model",
                        "parts": [{"text": "Đã hiểu rõ. Tôi là Security Presales Copilot và sẽ trả lời đúng chuẩn 8 phần Presales."}]
                    })
                
                contents.append({
                    "role": "user",
                    "parts": [{"text": prompt}]
                })

                payload = {
                    "contents": contents,
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": 2048,
                    }
                }

                async with httpx.AsyncClient(timeout=45.0) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"]
                    else:
                        print(f"Gemini API returned status {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"Gemini API call notice ({e}).")

        # 2. Try OpenAI if selected and API key exists
        if (provider == "openai" or openai_key) and openai_key and not openai_key.startswith("your_openai"):
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=openai_key)
                
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                print(f"OpenAI API call failed ({e}). Falling back to Ollama or Presales Engine.")

        # 2. Try Ollama if selected or as secondary provider
        if provider == "ollama" or ollama_url:
            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    ollama_payload = {
                        "model": settings.OLLAMA_MODEL,
                        "prompt": f"{system_prompt}\n\nUser Question:\n{prompt}" if system_prompt else prompt,
                        "stream": False,
                        "options": {"temperature": temperature}
                    }
                    resp = await client.post(f"{ollama_url.rstrip('/')}/api/generate", json=ollama_payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data.get("response", "")
            except Exception as e:
                print(f"Ollama call notice ({e}). Falling back to Presales Native Engine.")

        # 3. Built-in Smart Presales Generator (Ensures 100% reliable responses)
        return LLMService._smart_presales_fallback_generator(intent_text or prompt, system_prompt, prompt)

    @staticmethod
    def _smart_presales_fallback_generator(prompt: str, system_prompt: Optional[str], full_prompt: Optional[str] = None) -> str:
        """
        Offline Presales Rule-based AI Engine.
        Detects comparison / follow-up intent before solution routing.
        """
        lower = prompt.lower().strip()

        # ── Comparison intent detection ───────────────────────────────────
        COMPARISON_SIGNALS = [
            # Vietnamese with diacritics
            "khác gì", "khác nhau", "so sánh", "khác biệt",
            "tốt hơn", "nên chọn", "hay là", "phân biệt", "điểm khác",
            # Vietnamese without diacritics (common in quick typing)
            "khac gi", "khac nhau", "so sanh", "khac biet",
            "tot hon", "nen chon", "hay la", "phan biet", "diem khac",
            # Universal
            " vs ", "vs.", "compare", "versus", "difference",
        ]
        if any(sig in lower for sig in COMPARISON_SIGNALS):

            # Detect which products are being compared
            products = []
            product_map = {
                "picus": "Picus Security (BAS/CTEM)",
                "scv": "Picus SCV (Security Control Validation)",
                "apv": "Picus APV (Attack Path Validation)",
                "bas": "BAS (Breach and Attack Simulation)",
                "netwrix": "Netwrix",
                "dspm": "DSPM (Data Security Posture Management)",
                "access analyzer": "Netwrix Access Analyzer",
                "graylog": "Graylog Security (SIEM)",
                "trend micro": "Trend Micro Vision One XDR",
                "forcepoint": "Forcepoint DSPM & DLP",
                "cymulate": "Cymulate",
                "attackiq": "AttackIQ",
            }
            detected = [label for key, label in product_map.items() if key in lower]

            if len(detected) >= 2:
                a, b = detected[0], detected[1]
            elif "scv" in lower and "apv" in lower:
                a, b = "Picus SCV (Security Control Validation)", "Picus APV (Attack Path Validation)"
            elif "scv" in lower:
                a, b = "Picus SCV", "Sản phẩm được so sánh"
            elif "apv" in lower:
                a, b = "Picus APV", "Sản phẩm được so sánh"
            else:
                a, b = "Sản phẩm A", "Sản phẩm B"

            # Special case: Picus SCV vs APV — well-known comparison
            if ("scv" in lower and "apv" in lower) or ("scv" in lower or "apv" in lower):
                return (
                    "## So sánh: Picus SCV vs Picus APV\n\n"
                    "Cả hai đều là module thuộc nền tảng **Picus Complete Security Validation**, nhưng phục vụ mục tiêu khác nhau:\n\n"
                    "### Điểm giống nhau\n"
                    "- Đều thuộc hệ sinh thái Picus Security và tích hợp chặt chẽ với nhau.\n"
                    "- Đều dùng framework MITRE ATT&CK để ánh xạ kỹ thuật tấn công.\n"
                    "- Đều cung cấp Mitigation Actions tự động cho Firewall, EDR, SIEM.\n\n"
                    "### Điểm khác biệt chính\n"
                    "| Tiêu chí | Picus SCV (Security Control Validation) | Picus APV (Attack Path Validation) |\n"
                    "|---|---|---|\n"
                    "| **Mục đích chính** | Kiểm tra xem thiết bị bảo mật (Firewall, EDR, SIEM) có **chặn được** kỹ thuật tấn công cụ thể không | Khám phá **đường tấn công** từ điểm xâm nhập đến tài sản quan trọng |\n"
                    "| **Góc nhìn** | Kiểm thử theo chiều **dọc** — độ hiệu quả của từng control | Phân tích theo chiều **ngang** — bề mặt tấn công toàn mạng |\n"
                    "| **Cách hoạt động** | Mô phỏng 14.000+ kỹ thuật tấn công thực tế 24/7 mà không gián đoạn hệ thống | Lập bản đồ tất cả đường đi của hacker trong mạng nội bộ |\n"
                    "| **Output chính** | Security Score, danh sách kiểm soát thất bại, hướng dẫn khắc phục | Attack Graph trực quan, Critical Asset Exposure, ưu tiên vá lỗi |\n"
                    "| **Đối tượng dùng** | SOC Team, Security Operations, Compliance | CISO, Red Team, Risk Management |\n\n"
                    "### Khi nào chọn Picus SCV?\n"
                    "- Khách hàng muốn **xác thực hiệu quả liên tục** của Firewall, EDR, SIEM hiện có.\n"
                    "- Cần thay thế Pentest định kỳ bằng kiểm thử tự động hàng ngày.\n"
                    "- Mục tiêu: tối ưu hóa ROI đầu tư bảo mật, đạt tuân thủ ISO/NĐ 13.\n\n"
                    "### Khi nào chọn Picus APV?\n"
                    "- Khách hàng cần hiểu toàn bộ **bề mặt tấn công** và rủi ro lateral movement.\n"
                    "- CISO muốn trình bày **Attack Graph** cho Ban Giám Đốc về rủi ro thực tế.\n"
                    "- Ưu tiên vá lỗi dựa trên mức độ nguy hiểm theo đường tấn công thực tế.\n\n"
                    "### Gợi ý tư vấn cho Presales\n"
                    "- Thường **bán kèm cả hai**: SCV để vận hành hàng ngày, APV để chiến lược dài hạn.\n"
                    "- Discovery question gợi ý: *\"Anh/chị muốn đo hiệu quả thiết bị đang có, hay muốn nhìn toàn cảnh đường hacker có thể đi trong mạng?\"*\n"
                    "- Nếu ngân sách giới hạn: bắt đầu với **SCV** (ROI rõ ràng hơn, dễ justify).\n\n"
                    "> ⚠️ *Lưu ý: Thông tin trên dựa trên kiến thức nền tảng về Picus. "
                    "Để có số liệu chính xác từ tài liệu nội bộ, hãy đảm bảo backend LLM đang kết nối hoặc tài liệu Picus đã được index vào Vector DB.*"
                )

            return (
                f"## So sánh: {a} vs {b}\n\n"
                "Kali0t chưa có đủ dữ liệu chi tiết từ tài liệu nội bộ để so sánh chính xác hai sản phẩm này.\n\n"
                "**Để nhận câu trả lời chính xác, hãy:**\n"
                "1. Đảm bảo backend LLM (Gemini / OpenAI) đang kết nối trong Settings.\n"
                "2. Upload tài liệu của cả hai sản phẩm vào Document Center.\n\n"
                "**Câu hỏi làm rõ:**\n"
                "1. Anh/chị đang muốn so sánh về tính năng kỹ thuật, chi phí, hay use case triển khai?\n"
                "2. Khách hàng đang cân nhắc mua một trong hai hay kết hợp cả hai?"
            )

        # ── Solution routing (presales pitch) ─────────────────────────────
        if any(w in lower for w in ["dữ liệu", "dspm", "nhạy cảm", "data", "phân loại", "định danh", "lộ lọt"]):
            return (
                "## Solution\n"
                "Netwrix DSPM (Data Security Posture Management) & Forcepoint DSPM\n\n"
                "## Category\n"
                "DSPM / Data Security & Compliance\n\n"
                "## Problem solved\n"
                "Giải quyết triệt để bài toán mù mờ dữ liệu (Dark Data), không biết dữ liệu nhạy cảm (PII, thẻ tín dụng, bí mật kinh doanh, mã nguồn) đang nằm rải rác ở đâu trên On-premise và Cloud (AWS, Azure, Google Drive, OneDrive, Database, File Servers), ai đang có quyền truy cập vượt mức và nguy cơ rò rỉ dữ liệu.\n\n"
                "## Key capability\n"
                "- Tự động quét (Data Discovery) và phân loại dữ liệu chính xác với AI/ML (Classification).\n"
                "- Đánh giá rủi ro tư thế dữ liệu (Posture Assessment) và chỉ ra các vị trí có quyền truy cập dư thừa (Over-privileged).\n"
                "- Giám sát và ngăn chặn hành vi truy cập dữ liệu bất thường theo thời gian thực.\n"
                "- Báo cáo tuân thủ tự động theo tiêu chuẩn Nghị định 13/2023/NĐ-CP, GDPR, PCI-DSS, HIPAA, ISO 27001.\n\n"
                "## Use case\n"
                "- Khách hàng chuẩn bị audit tuân thủ Nghị định 13 bảo vệ dữ liệu cá nhân.\n"
                "- Khách hàng dịch chuyển dữ liệu lên Multi-Cloud cần kiểm soát toàn diện bề mặt dữ liệu.\n"
                "- Phát hiện và thu hồi quyền truy cập của nhân viên đã nghỉ việc vào các thư mục chứa dữ liệu nhạy cảm.\n\n"
                "## Customer discovery questions\n"
                "1. Hiện tại tổ chức của anh/chị có bao nhiêu phần trăm dữ liệu nhạy cảm được phân loại rõ ràng?\n"
                "2. Doanh nghiệp đang lưu trữ dữ liệu chính ở On-premise, File Server hay các dịch vụ Cloud như M365, AWS, GCP?\n"
                "3. Khi có yêu cầu kiểm toán tuân thủ Nghị định 13 hoặc ISO 27001, đội ngũ mất bao lâu để xuất báo cáo kiểm kê dữ liệu?\n\n"
                "## Competitor / Alternative\n"
                "- Forcepoint DSPM, Varonis Data Security Platform, Microsoft Purview, BigID\n\n"
                "## Source reference\n"
                "Document: Security Brochure_update Jul 2026.pdf / Netwrix DSPM.pdf\n"
                "Page: 12-18"
            )
        
        elif any(w in lower for w in ["picus", "bas", "hacker", "kiểm tra", "vượt qua", "tấn công", "mô phỏng", "mitre", "ctem"]):
            return (
                "## Solution\n"
                "Picus Security (Breach and Attack Simulation - BAS)\n\n"
                "## Category\n"
                "BAS (Breach and Attack Simulation) & CTEM (Continuous Threat Exposure Management)\n\n"
                "## Problem solved\n"
                "Giải quyết thách thức 'Không biết hệ thống phòng thủ có thực sự chặn được hacker hay không'. Doanh nghiệp đầu tư nhiều tường lửa, EDR, SIEM nhưng không đo lường được hiệu quả thực tế và độ sẵn sàng trước các kỹ thuật tấn công mới nhất.\n\n"
                "## Key capability\n"
                "- Mô phỏng tự động và liên tục 24/7 hàng nghìn kịch bản tấn công thực tế (ransomware, APT, malware, data exfiltration) mà không gây gián đoạn hệ thống.\n"
                "- Ánh xạ chi tiết 100% theo ma trận MITRE ATT&CK Framework.\n"
                "- Cung cấp hướng dẫn khắc phục tức thì (Mitigation Actions) tự động cho Tường lửa (Palo Alto, Fortinet, Check Point), WAF, EDR và SIEM.\n"
                "- Tích hợp chỉ số sẵn sàng phòng thủ (Security Score) trực quan cho CISO và Ban Giám Đốc.\n\n"
                "## Use case\n"
                "- Kiểm tra tự động hiệu quả của giải pháp SOC, SIEM và EDR định kỳ hàng ngày thay vì chờ Pentest 1 năm/lần.\n"
                "- Xác thực chính sách tường lửa và WAF có chặn được các lỗ hổng zero-day mới phát hiện không.\n"
                "- Đo lường và tối ưu hóa chi phí đầu tư bảo mật (ROI Optimization).\n\n"
                "## Customer discovery questions\n"
                "1. Hiện tại đơn vị đo lường hiệu quả hoạt động của các thiết bị bảo mật (Firewall, EDR, SIEM) bằng cách nào?\n"
                "2. Tần suất thực hiện Pentest / Red Teaming hiện tại là bao lâu một lần (6 tháng hay 1 năm)?\n"
                "3. Khi xuất hiện một biến thể Ransomware mới, mất bao lâu để anh/chị biết hệ thống của mình có chặn được hay không?\n\n"
                "## Competitor / Alternative\n"
                "- Cymulate, AttackIQ, SafeBreach, Mandiant Security Validation\n\n"
                "## Source reference\n"
                "Document: Security Brochure_update Jul 2026.pdf / Picus Solution Brief.pdf\n"
                "Page: 4-9"
            )
            
        elif any(w in lower for w in ["quyền", "access", "analyzer", "identity", "active directory", "ad", "đặc quyền"]):
            return (
                "## Solution\n"
                "Netwrix Access Analyzer (Privilege & Identity Governance)\n\n"
                "## Category\n"
                "Identity & Access Governance / Active Directory Security\n\n"
                "## Problem solved\n"
                "Giải quyết tình trạng leo thang đặc quyền (Privilege Creep), tài khoản mồ côi (Orphan Accounts), nhóm lồng nhau (Nested Groups) phức tạp trong Active Directory / Entra ID dẫn đến rủi ro lộ lọt thông tin và tấn công nội bộ.\n\n"
                "## Key capability\n"
                "- Tự động lập bản đồ ai có quyền truy cập vào tài nguyên nào (Effective Permissions).\n"
                "- Phân tích và gỡ bỏ quyền truy cập dư thừa theo nguyên tắc đặc quyền tối thiểu (Least Privilege).\n"
                "- Phát hiện tài khoản quản trị không hoạt động hoặc tài khoản chia sẻ dùng chung.\n"
                "- Mô phỏng thay đổi chính sách trước khi áp dụng để tránh gián đoạn dịch vụ.\n\n"
                "## Use case\n"
                "- Dọn dẹp cấu trúc phân quyền Active Directory cho doanh nghiệp sau sáp nhập hoặc mở rộng quy mô.\n"
                "- Rà soát định kỳ quyền truy cập vào các thư mục chứa dữ liệu tài chính kế toán, nhân sự.\n"
                "- Đạt chứng chỉ tuân thủ SOX, ISO 27001 về kiểm soát truy cập định danh.\n\n"
                "## Customer discovery questions\n"
                "1. Doanh nghiệp đang quản lý quyền hạn truy cập của người dùng trên Active Directory hay Cloud ID như thế nào?\n"
                "2. Anh/chị có thể xác định ngay lập tức một nhân viên cụ thể có quyền xem/sửa những file nào trong hệ thống không?\n"
                "3. Quy trình thu hồi quyền truy cập khi nhân viên chuyển phòng ban hoặc nghỉ việc hiện có tự động không?\n\n"
                "## Competitor / Alternative\n"
                "- SailPoint IdentityIQ, Quest Active Roles, ManageEngine ADManager Plus\n\n"
                "## Source reference\n"
                "Document: Netwrix Access Analyzer.pdf\n"
                "Page: 2-8"
            )

        elif any(w in lower for w in ["soc", "siem", "log", "graylog", "giám sát", "cảnh báo"]):
            return (
                "## Solution\n"
                "Graylog Security & Trend Micro Vision One XDR\n\n"
                "## Category\n"
                "SOC / SIEM / Centralized Log Management & Analytics\n\n"
                "## Problem solved\n"
                "Giải quyết tình trạng quá tải cảnh báo (Alert Fatigue), chi phí lưu trữ log khổng lồ, thiếu khả năng phân tích tương quan để phát hiện các cuộc tấn công tinh vi trong môi trường Hybrid.\n\n"
                "## Key capability\n"
                "- Thu thập và chuẩn hóa tập trung hàng terabyte log/ngày với tốc độ cao và chi phí tối ưu.\n"
                "- Tích hợp Threat Intelligence và quy tắc tương quan phát hiện hành vi dị thường (UEBA).\n"
                "- Giao diện điều tra sự cố (Threat Hunting) trực quan, tìm kiếm log trong vài mili-giây.\n"
                "- Tích hợp điều phối phản hồi tự động (SOAR / Incident Response).\n\n"
                "## Use case\n"
                "- Xây dựng trung tâm điều hành an ninh mạng (SOC) nội bộ với chi phí TCO linh hoạt.\n"
                "- Đáp ứng yêu cầu lưu trữ log tập trung phục vụ điều tra số (Forensics) và tuân thủ pháp luật.\n\n"
                "## Customer discovery questions\n"
                "1. Tổng dung lượng log/ngày mà hệ thống của anh/chị cần thu thập là khoảng bao nhiêu GB?\n"
                "2. Đội ngũ SOC mất bao lâu để điều tra nguyên nhân gốc rễ khi có một cảnh báo an ninh xuất hiện?\n"
                "3. Các giải pháp SIEM hiện tại có đáp ứng được về mặt ngân sách khi lượng log tăng trưởng hàng năm?\n\n"
                "## Competitor / Alternative\n"
                "- Splunk Enterprise Security, Elastic Security, IBM QRadar, Microsoft Sentinel\n\n"
                "## Source reference\n"
                "Document: Security Brochure_update Jul 2026.pdf / Certus Solution.pdf\n"
                "Page: 8-14"
            )

        # Do not select a solution for an ambiguous question. Ask a focused
        # clarification instead of producing a plausible but irrelevant pitch.
        return (
            "## Solution\nChưa xác định\n\n"
            "## Category\nCần làm rõ nhu cầu\n\n"
            "## Problem solved\n"
            "Câu hỏi hiện chưa đủ thông tin để chọn đúng giải pháp mà không suy đoán.\n\n"
            "## Key capability\n"
            "- Kali0t sẽ chỉ đề xuất giải pháp sau khi xác định đúng bài toán.\n\n"
            "## Use case\n"
            "- Hãy mô tả hệ thống, loại dữ liệu hoặc sự cố mà anh/chị đang cần xử lý.\n\n"
            "## Customer discovery questions\n"
            "1. Anh/chị cần bảo vệ dữ liệu, kiểm tra khả năng phòng thủ, quản trị quyền hay giám sát log?\n"
            "2. Môi trường chính là On-premise, Cloud hay Hybrid?\n"
            "3. Mục tiêu ưu tiên và tiêu chí lựa chọn giải pháp là gì?\n\n"
            "## Competitor / Alternative\n"
            "- Chưa xác định khi chưa rõ nhu cầu\n\n"
            "## Source reference\n"
            "Document: Chưa có nguồn đủ phù hợp\n"
            "Page: N/A"
        )
