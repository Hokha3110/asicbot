import os
import shutil
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.solution import Solution
from app.models.battlecard import BattleCard
from app.models.quiz import QuizQuestion
from app.models.document import Document
from app.utils.security import get_password_hash
from app.services.doc_parser import DocumentParserService
from app.services.vector_service import vector_service
from app.config import settings

def seed_database(db: Session):
    print("Starting database seeding & initial data import...")

    # 1. Seed Users
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(
            username="admin",
            email="admin@securitycopilot.internal",
            hashed_password=get_password_hash("Admin@123456"),
            full_name="Senior Presales Administrator",
            role="admin"
        )
        db.add(admin)

    if not db.query(User).filter(User.username == "presales_user").first():
        user = User(
            username="presales_user",
            email="presales@securitycopilot.internal",
            hashed_password=get_password_hash("Presales@123"),
            full_name="Nguyen Van Presales",
            role="user"
        )
        db.add(user)

    db.commit()

    # 2. Seed Solutions
    solutions_data = [
        {
            "name": "Picus Complete Security Validation",
            "vendor": "Picus Security",
            "category": "BAS",
            "problem": "Doanh nghiệp không biết các thiết bị bảo mật hiện tại (Firewall, WAF, EDR, SIEM) có thực sự chặn được các cuộc tấn công và kỹ thuật hacker mới nhất hay không. Kiểm thử truyền thống (Pentest) chỉ diễn ra 1-2 lần/năm và nhanh chóng lỗi thời.",
            "description": "Giải pháp Mô phỏng Tấn công và Xâm nhập liên tục (Breach and Attack Simulation - BAS) hàng đầu thế giới, tự động hóa kiểm tra thế trận phòng thủ 24/7 theo khung MITRE ATT&CK.",
            "features": [
                "Continuous Threat Exposure Management (CTEM)",
                "Mô phỏng hơn 4,000+ kịch bản tấn công thực tế và Ransomware mới nhất",
                "Tự động sinh cấu hình khắc phục (Prevention & Detection Signatures) cho Palo Alto, Fortinet, Check Point, Splunk, Elastic",
                "Chỉ số Security Score định lượng theo thời gian thực"
            ],
            "use_case": [
                "Xác thực tự động hiệu quả của Tường lửa & EDR định kỳ hàng ngày",
                "Đánh giá năng lực phát hiện sự cố của SOC / SIEM",
                "Báo cáo đo lường ROI đầu tư bảo mật cho Hội đồng Quản trị"
            ],
            "competitor": ["Cymulate", "AttackIQ", "SafeBreach", "Mandiant Security Validation"],
            "keywords": ["BAS", "MITRE ATT&CK", "CTEM", "Breach Attack Simulation", "Picus", "Mô phỏng tấn công", "Hacker", "Kiểm tra phòng thủ", "Pentest"],
            "discovery_questions": [
                "Hiện tại đơn vị đo lường hiệu quả hoạt động của các thiết bị bảo mật bằng cách nào?",
                "Tần suất thực hiện Pentest / Red Teaming hiện tại là bao lâu một lần?",
                "Khi xuất hiện một biến thể Ransomware mới trên thế giới, mất bao lâu để anh/chị biết hệ thống của mình có chặn được hay không?"
            ],
            "documents": [{"document_name": "Security Brochure_update Jul 2026.pdf", "pages": [4, 5, 6]}]
        },
        {
            "name": "Netwrix DSPM (Data Security Posture Management)",
            "vendor": "Netwrix Corporation",
            "category": "DSPM",
            "problem": "Doanh nghiệp bị mất kiểm soát dữ liệu nhạy cảm (PII, số CCCD, thẻ tín dụng, hợp đồng, mã nguồn) nằm rải rác trên Cloud (OneDrive, AWS S3, Google Drive, M365) và File Server On-premise, đối mặt với nguy cơ bị phạt nặng theo Nghị định 13/2023/NĐ-CP và rò rỉ dữ liệu.",
            "description": "Nền tảng Quản trị Tư thế Bảo mật Dữ liệu (DSPM) tự động quét, định danh, phân loại và bảo vệ dữ liệu nhạy cảm trên toàn bộ hạ tầng Multi-Cloud và On-Premise.",
            "features": [
                "Tự động khám phá (Data Discovery) và phân loại dữ liệu nhạy cảm bằng AI/ML",
                "Phân tích quyền hạn truy cập dư thừa (Excessive Permissions) và gỡ bỏ quyền không an toàn",
                "Phát hiện và ngăn chặn hành vi bất thường đối với dữ liệu nhạy cảm theo thời gian thực",
                "Báo cáo tuân thủ sẵn có cho Nghị định 13/2023, GDPR, HIPAA, PCI-DSS, ISO 27001"
            ],
            "use_case": [
                "Kiểm kê và phân loại dữ liệu cá nhân phục vụ kiểm toán Nghị định 13",
                "Thu hồi quyền truy cập của nhân sự đã chuyển phòng ban hoặc nghỉ việc",
                "Kiểm soát dữ liệu khi chuyển dịch lên Cloud M365 / AWS"
            ],
            "competitor": ["Forcepoint DSPM", "Varonis Data Security Platform", "Microsoft Purview", "BigID"],
            "keywords": ["DSPM", "Data Security Posture", "Bảo vệ dữ liệu", "Phân loại dữ liệu", "Nghị định 13", "Data Classification", "PII", "Netwrix"],
            "discovery_questions": [
                "Hiện tại tổ chức có biết chính xác dữ liệu nhạy cảm của khách hàng và nhân viên đang được lưu trữ ở những đâu không?",
                "Khi cơ quan quản lý yêu cầu kiểm toán tuân thủ Nghị định 13, đội ngũ mất bao lâu để lập danh mục kiểm kê dữ liệu?",
                "Làm thế nào để anh/chị phát hiện khi một tài khoản tải về số lượng lớn file nhạy cảm trong thời gian ngắn?"
            ],
            "documents": [{"document_name": "Netwrix DSPM.pdf", "pages": [1, 2, 3, 4]}]
        },
        {
            "name": "Netwrix Access Analyzer",
            "vendor": "Netwrix Corporation",
            "category": "Identity",
            "problem": "Tình trạng leo thang đặc quyền (Privilege Creep), tài khoản ẩn danh, nhóm người dùng lồng nhau phức tạp trong Active Directory / Entra ID khiến kẻ tấn công dễ dàng chiếm đoạt Domain Controller và di chuyển ngang (Lateral Movement).",
            "description": "Giải pháp Quản trị Quyền Truy cập và Định danh (Identity & Access Governance) giúp phân tích toàn diện ma trận quyền hạn thực tế (Effective Permissions) và áp dụng nguyên tắc Đặc quyền tối thiểu (Least Privilege).",
            "features": [
                "Lập bản đồ trực quan Effective Permissions trên toàn bộ Active Directory và File Servers",
                "Phát hiện tài khoản mồ côi (Orphan Accounts) và tài khoản có mật khẩu không bao giờ hết hạn",
                "Mô phỏng thay đổi (What-if Analysis) trước khi thu hồi quyền để đảm bảo không gián đoạn kinh doanh",
                "Tự động hóa dọn dẹp nhóm bảo mật và cấp quyền Just-In-Time"
            ],
            "use_case": [
                "Chuẩn hóa và làm sạch hệ thống phân quyền Active Directory doanh nghiệp lớn",
                "Bảo vệ tài khoản quản trị Domain Admins trước các kỹ thuật Pass-the-Hash / Kerberoasting",
                "Kiểm toán phân quyền truy cập định kỳ cho ngân hàng và tổ chức tài chính"
            ],
            "competitor": ["SailPoint IdentityIQ", "Quest Active Roles", "ManageEngine ADAudit Plus"],
            "keywords": ["Access Analyzer", "Active Directory", "Least Privilege", "Phân quyền", "Đặc quyền", "Identity Governance", "Netwrix"],
            "discovery_questions": [
                "Doanh nghiệp đang quản lý và rà soát quyền hạn người dùng trên Active Directory bằng cách thủ công hay có công cụ tự động?",
                "Anh/chị có thể xác định ngay một nhân viên có quyền truy cập vào những dữ liệu nào chỉ với 1 click chuột không?",
                "Chính sách thu hồi tài khoản và quyền của người dùng nghỉ việc mất bao lâu để thực thi hoàn tất?"
            ],
            "documents": [{"document_name": "Netwrix Access Analyzer.pdf", "pages": [1, 2, 3]}]
        },
        {
            "name": "Certus Solution",
            "vendor": "Certus Cybersecurity",
            "category": "DevSecOps",
            "problem": "Doanh nghiệp phát triển phần mềm nhanh nhưng bỏ quên kiểm tra bảo mật mã nguồn và container, dẫn đến các lỗ hổng nghiêm trọng bị đẩy lên môi trường Production.",
            "description": "Giải pháp đánh giá an toàn thông tin toàn diện, quét mã nguồn (SAST/DAST) và kiểm định tuân thủ bảo mật hạ tầng đám mây Cloud Security Posture.",
            "features": [
                "Tích hợp quét bảo mật tự động vào CI/CD Pipeline (GitLab, GitHub, Jenkins)",
                "Phân tích thành phần mã nguồn mở (SCA) phát hiện lỗ hổng thư viện phụ thuộc",
                "Kiểm tra bảo mật API và kiến trúc Microservices",
                "Báo cáo chi tiết vị trí dòng code có lỗ hổng và hướng dẫn sửa lỗi (Remediation Code)"
            ],
            "use_case": [
                "Triển khai quy trình DevSecOps cho các đội ngũ Agile / Scrum",
                "Kiểm định an toàn bảo mật cho các ứng dụng Mobile Banking và E-Commerce",
                "Đạt tiêu chuẩn OWASP Top 10 và PCI-DSS cho mã nguồn thanh toán"
            ],
            "competitor": ["Checkmarx", "Veracode", "Snyk", "SonarQube Enterprise"],
            "keywords": ["Certus", "DevSecOps", "SAST", "DAST", "SCA", "Bảo mật mã nguồn", "OWASP"],
            "discovery_questions": [
                "Quy trình kiểm thử bảo mật ứng dụng hiện tại diễn ra trước khi release hay sau khi đã golive?",
                "Đội ngũ phát triển mất bao lâu để phát hiện và vá một lỗ hổng trong thư viện mã nguồn mở bên thứ ba?"
            ],
            "documents": [{"document_name": "Certus Solution.pdf", "pages": [1, 2]}]
        },
        {
            "name": "Graylog Security & SOC Operations",
            "vendor": "Graylog Inc.",
            "category": "SOC",
            "problem": "Các giải pháp SIEM truyền thống quá đắt đỏ khi tính phí theo dung lượng log nạp vào (GB/day), khó mở rộng và thời gian tìm kiếm điều tra sự cố mất hàng chục phút.",
            "description": "Nền tảng SIEM & Phân tích Log thế hệ mới với hiệu năng tìm kiếm siêu tốc, chi phí TCO tối ưu và tích hợp sẵn Threat Intelligence.",
            "features": [
                "Thu thập và phân tích hàng Terabyte log mỗi ngày với tốc độ mili-giây",
                "Bộ quy tắc phát hiện tấn công và phân tích hành vi dị thường (UEBA) có sẵn",
                "Giao diện điều tra sự cố (Threat Hunting Dashboards) linh hoạt",
                "Tích hợp điều phối phản hồi sự cố (SOAR) tự động khóa IP/User"
            ],
            "use_case": [
                "Xây dựng trung tâm điều hành an ninh mạng (SOC) tập trung cho doanh nghiệp",
                "Lưu trữ và điều tra log phục vụ kiểm toán và điều tra số (Forensics)",
                "Giảm 70% chi phí lưu trữ log so với SIEM truyền thống"
            ],
            "competitor": ["Splunk Enterprise Security", "Elastic Security", "IBM QRadar", "Microsoft Sentinel"],
            "keywords": ["Graylog", "SIEM", "SOC", "Log Management", "Threat Hunting", "UEBA", "Giám sát an ninh"],
            "discovery_questions": [
                "Tổng lượng log sinh ra mỗi ngày từ mạng lưới và máy chủ của doanh nghiệp là bao nhiêu?",
                "Chi phí bản quyền SIEM hiện tại có đang là rào cản khi mở rộng hệ thống không?"
            ],
            "documents": [{"document_name": "Security Brochure_update Jul 2026.pdf", "pages": [8, 9, 10]}]
        },
        {
            "name": "Trend Micro Vision One XDR",
            "vendor": "Trend Micro",
            "category": "XDR",
            "problem": "Các cảnh báo an ninh nằm phân mảnh ở Endpoint, Server, Email và Network mà không có sự liên kết tương quan, khiến đội ngũ SOC mất nhiều thời gian để xâu chuỗi sự cố.",
            "description": "Nền tảng Extended Detection & Response (XDR) tích hợp đa tầng bảo vệ toàn diện từ Endpoint, Email, Server, Cloud Workload đến Mạng.",
            "features": [
                "Tương quan cảnh báo tự động trên đa vector tấn công (Email, Endpoint, Network, Cloud)",
                "AI/ML phát hiện các chiến dịch tấn công có chủ đích APT tinh vi",
                "Hành động phản hồi 1-click (Cô lập máy tính, thu hồi email độc hại, chặn IP)",
                "Tích hợp Managed XDR (MDR) hỗ trợ giám sát 24/7 từ chuyên gia hãng"
            ],
            "use_case": [
                "Phát hiện và ngăn chặn các cuộc tấn công lừa đảo Email qua mặt Gateway",
                "Bảo vệ máy chủ Cloud AWS/Azure và Container Kubernetes",
                "Tối ưu hóa thời gian phát hiện và xử lý sự cố (MTTD / MTTR)"
            ],
            "competitor": ["CrowdStrike Falcon", "SentinelOne Singularity", "Microsoft Defender for Endpoint"],
            "keywords": ["Trend Micro", "XDR", "EDR", "Vision One", "Phát hiện tấn công", "Endpoint Security"],
            "discovery_questions": [
                "Đội ngũ an ninh hiện tại mất bao lâu để cô lập một máy tính bị nhiễm mã độc trong mạng?",
                "Hệ thống bảo vệ Endpoint và Email của anh/chị có liên kết cảnh báo với nhau không?"
            ],
            "documents": [{"document_name": "Security Brochure_update Jul 2026.pdf", "pages": [14, 15, 16]}]
        },
        {
            "name": "Forcepoint DSPM & DLP",
            "vendor": "Forcepoint",
            "category": "DSPM",
            "problem": "Rò rỉ dữ liệu qua kênh Web, Email, USB, Cloud Storage và thiếu khả năng giám sát mức độ rủi ro dữ liệu theo ngữ cảnh thời gian thực.",
            "description": "Bộ giải pháp Ngăn chặn thất thoát dữ liệu (DLP) và Quản trị tư thế dữ liệu (DSPM) bảo vệ dữ liệu ở mọi trạng thái (Data in-use, in-motion, at-rest).",
            "features": [
                "Nhận diện vân tay dữ liệu chính xác (Exact Data Matching - EDM)",
                "Bảo vệ dữ liệu trên ứng dụng Cloud (CASB) và thiết bị đầu cuối (Endpoint DLP)",
                "Kiểm soát truy cập dựa trên điểm rủi ro hành vi người dùng (Risk-Adaptive Protection)",
                "Chính sách tuân thủ tuân theo các khung chuẩn quốc tế"
            ],
            "use_case": [
                "Chặn nhân viên sao chép mã nguồn hoặc cơ sở dữ liệu khách hàng ra USB",
                "Ngăn chặn gửi thông tin thẻ ngân hàng hoặc CCCD qua email ngoài tổ chức",
                "Kiểm soát dữ liệu đẩy lên các dịch vụ AI công cộng như ChatGPT"
            ],
            "competitor": ["Symantec DLP", "Digital Guardian", "Trellix DLP", "Netwrix DSPM"],
            "keywords": ["Forcepoint", "DLP", "DSPM", "Chống thất thoát dữ liệu", "Bảo vệ dữ liệu", "CASB"],
            "discovery_questions": [
                "Doanh nghiệp đã có chính sách kiểm soát việc chia sẻ dữ liệu nhạy cảm lên ChatGPT hay Cloud chưa?",
                "Có cơ chế nào ngăn chặn việc copy dữ liệu ra USB hoặc in ấn tài liệu mật không?"
            ],
            "documents": [{"document_name": "Security Brochure_update Jul 2026.pdf", "pages": [11, 12, 13]}]
        }
    ]

    for item in solutions_data:
        existing_sol = db.query(Solution).filter(Solution.name == item["name"]).first()
        if not existing_sol:
            sol_obj = Solution(**item)
            db.add(sol_obj)

    db.commit()

    # 3. Seed Battle Cards
    battlecards_data = [
        {
            "solution_name": "Picus Complete Security Validation",
            "vendor": "Picus Security",
            "category": "BAS",
            "overview": "Picus Security là giải pháp BAS tiên phong giúp kiểm tra liên tục 24/7 năng lực phòng thủ thực tế của hệ thống bảo mật theo khung MITRE ATT&CK mà không gây gián đoạn.",
            "why_customer_needs": "Doanh nghiệp đã chi hàng triệu USD cho Firewall, EDR, SIEM nhưng không biết cấu hình đã chuẩn chưa và có chặn được ransomware mới nổi hay không.",
            "pain_points": [
                "Pentest truyền thống chỉ phản ánh tại 1 thời điểm và tốn kém chi phí.",
                "Cấu hình thiết bị bảo mật bị sai lệch (Configuration Drift) theo thời gian.",
                "Không có số liệu định lượng chứng minh hiệu quả đầu tư bảo mật cho C-Level."
            ],
            "talking_points": [
                "Mô phỏng an toàn 100% không ảnh hưởng đến dữ liệu sản xuất (Production-safe).",
                "Tự động sinh bộ lọc cấu hình (Mitigation rules) cho Firewall/WAF chỉ với 1 click.",
                "Giúp tối ưu hóa toàn bộ các giải pháp bảo mật hiện có của khách hàng."
            ],
            "technical_advantages": [
                "Hơn 4,000+ kịch bản tấn công cập nhật hàng ngày bởi Picus Labs.",
                "Tích hợp Native API 2 chiều với hơn 50+ hãng bảo mật hàng đầu.",
                "Kiến trúc Agentless / Lightweight Sensor triển khai trong 30 phút."
            ],
            "common_objections": [
                {
                    "objection": "Chúng tôi đã thuê dịch vụ Pentest hàng năm rồi thì cần gì BAS?",
                    "answer": "Pentest giống như đi khám sức khỏe định kỳ 1 năm/lần, còn Picus BAS như thiết bị theo dõi nhịp tim 24/7 giúp phát hiện ngay lỗ hổng phòng thủ vừa phát sinh."
                },
                {
                    "objection": "Mô phỏng tấn công có làm sập hệ thống hoặc làm gián đoạn mạng không?",
                    "answer": "Picus sử dụng các gói tin tấn công mô phỏng an toàn (Non-destructive payloads), đã được kiểm chứng tại hàng trăm ngân hàng và tổ chức chính phủ trên thế giới."
                }
            ],
            "target_buyer_personas": ["CISO", "SOC Lead", "Security Architect", "IT Director"]
        },
        {
            "solution_name": "Netwrix DSPM",
            "vendor": "Netwrix Corporation",
            "category": "DSPM",
            "overview": "Netwrix DSPM giải quyết triệt để vấn đề mất kiểm soát dữ liệu nhạy cảm trên On-premise và Cloud, tự động phân loại và giảm thiểu rủi ro bảo mật dữ liệu.",
            "why_customer_needs": "Nghị định 13/2023/NĐ-CP phạt tới 5% doanh thu nếu để lộ lọt dữ liệu cá nhân. Doanh nghiệp cần công cụ tự động lập danh mục và bảo vệ dữ liệu.",
            "pain_points": [
                "Dữ liệu phân tán trên OneDrive, Google Drive, File Server mà IT không nắm được (Dark Data).",
                "Phân quyền lỏng lẻo khiến nhân viên dễ dàng xem trộm tài liệu mật.",
                "Kiểm toán thủ công mất hàng tháng và dễ bỏ sót."
            ],
            "talking_points": [
                "Quét và phân loại chính xác tới 99% dữ liệu cá nhân Việt Nam (CCCD, MST, Số tài khoản).",
                "Giảm thiểu bề mặt tấn công dữ liệu (Data Attack Surface) ngay lập tức.",
                "Cung cấp báo cáo sẵn sàng kiểm toán Nghị định 13 chỉ trong 5 phút."
            ],
            "technical_advantages": [
                "Khả năng đọc hiểu ngữ cảnh tài liệu (Content & Context Analysis) bằng AI.",
                "Không cần cài agent phức tạp trên mọi máy trạm.",
                "Tốc độ quét dữ liệu hàng chục terabyte mỗi ngày với tài nguyên tối thiểu."
            ],
            "common_objections": [
                {
                    "objection": "Chúng tôi đã có Microsoft 365 DLP rồi thì cần thêm DSPM làm gì?",
                    "answer": "M365 DLP chỉ bảo vệ trên môi trường Microsoft Cloud. Netwrix DSPM bao phủ toàn diện cả File Server On-prem, cơ sở dữ liệu SQL/Oracle, AWS S3 và Google Workspace, đồng thời quản trị quyền truy cập sâu hơn."
                }
            ],
            "target_buyer_personas": ["CISO", "Data Protection Officer (DPO)", "Legal & Compliance", "CIO"]
        }
    ]

    for item in battlecards_data:
        existing_bc = db.query(BattleCard).filter(BattleCard.solution_name == item["solution_name"]).first()
        if not existing_bc:
            bc_obj = BattleCard(**item)
            db.add(bc_obj)

    db.commit()

    # 4. Seed Security Academy Quiz Questions
    quiz_questions_data = [
        {
            "solution_name": "Picus Complete Security Validation",
            "category": "BAS",
            "question_text": "Giải pháp Picus Security thuộc nhóm giải pháp nào trong các phân loại an toàn thông tin dưới đây?",
            "options": ["SIEM (Security Information & Event Management)", "BAS (Breach and Attack Simulation)", "DLP (Data Loss Prevention)", "PAM (Privileged Access Management)"],
            "correct_option_index": 1,
            "explanation": "Picus Security là giải pháp hàng đầu thế giới trong nhóm BAS (Breach & Attack Simulation), chuyên mô phỏng liên tục các kỹ thuật tấn công theo khung MITRE ATT&CK để kiểm tra hiệu quả phòng thủ.",
            "difficulty": "Easy",
            "is_daily_challenge": True
        },
        {
            "solution_name": "Netwrix DSPM",
            "category": "DSPM",
            "question_text": "Khi khách hàng cần tuân thủ Nghị định 13/2023/NĐ-CP về Bảo vệ dữ liệu cá nhân và cần biết dữ liệu CCCD, tài khoản ngân hàng đang nằm ở đâu, giải pháp nào phù hợp nhất?",
            "options": ["Netwrix DSPM", "Graylog SIEM", "Certus DevSecOps", "Trend Micro XDR"],
            "correct_option_index": 0,
            "explanation": "Netwrix DSPM (Data Security Posture Management) chuyên quét, phát hiện, phân loại dữ liệu nhạy cảm (CCCD, thẻ ngân hàng, PII) và quản trị rủi ro tư thế dữ liệu theo quy định pháp luật.",
            "difficulty": "Easy",
            "is_daily_challenge": True
        },
        {
            "solution_name": "Netwrix Access Analyzer",
            "category": "Identity",
            "question_text": "Nguyên tắc 'Least Privilege' (Đặc quyền tối thiểu) trong bảo mật định danh Active Directory nhằm mục đích gì?",
            "options": ["Cấp quyền Admin toàn quyền cho tất cả nhân viên IT", "Chỉ cấp cho người dùng những quyền hạn tối thiểu cần thiết để hoàn thành công việc", "Tự động xóa tất cả tài khoản người dùng sau 30 ngày", "Mã hóa toàn bộ ổ cứng của Domain Controller"],
            "correct_option_index": 1,
            "explanation": "Nguyên tắc Đặc quyền tối thiểu (Least Privilege) đảm bảo người dùng chỉ có quyền hạn tối thiểu đủ để làm việc, giảm thiểu tối đa rủi ro khi tài khoản bị tấn công hoặc chiếm quyền.",
            "difficulty": "Medium",
            "is_daily_challenge": True
        },
        {
            "solution_name": "Graylog Security",
            "category": "SOC",
            "question_text": "Ưu điểm nổi bật nhất của Graylog SIEM so với các giải pháp SIEM truyền thống trong môi trường doanh nghiệp là gì?",
            "options": ["Miễn phí phần cứng máy chủ", "Tốc độ tìm kiếm log cực nhanh và tối ưu chi phí TCO khi lưu trữ dung lượng log lớn", "Thay thế hoàn toàn Firewall và EDR", "Chỉ chạy được trên máy tính Windows cá nhân"],
            "correct_option_index": 1,
            "explanation": "Graylog nổi tiếng với khả năng xử lý hàng Terabyte log mỗi ngày với hiệu năng truy vấn mili-giây và mô hình chi phí TCO linh hoạt, không gây gánh nặng tài chính như các giải pháp tính theo dung lượng log.",
            "difficulty": "Medium",
            "is_daily_challenge": True
        },
        {
            "solution_name": "Trend Micro Vision One XDR",
            "category": "XDR",
            "question_text": "Khái niệm XDR (Extended Detection and Response) khác với EDR (Endpoint Detection and Response) ở điểm nào?",
            "options": ["XDR chỉ bảo vệ điện thoại di động", "XDR mở rộng tương quan cảnh báo từ nhiều vector (Endpoint, Email, Network, Cloud Server) thay vì chỉ ở máy trạm Endpoint", "XDR không cần kết nối Internet", "EDR có tính năng tự động diệt virus còn XDR thì không"],
            "correct_option_index": 1,
            "explanation": "XDR mở rộng phạm vi giám sát và tương quan dữ liệu từ Endpoint sang Email, Server, Cloud Workloads và Network, giúp phát hiện chuỗi tấn công đa vector toàn diện.",
            "difficulty": "Hard",
            "is_daily_challenge": True
        }
    ]

    for item in quiz_questions_data:
        existing_q = db.query(QuizQuestion).filter(QuizQuestion.question_text == item["question_text"]).first()
        if not existing_q:
            q_obj = QuizQuestion(**item)
            db.add(q_obj)

    db.commit()

    # 5. Auto Import & Parse Existing Files (e.g. Security Brochure_update Jul 2026.pdf)
    _auto_import_existing_documents(db)
    print("Database seeding & initial data import completed successfully!")

def _auto_import_existing_documents(db: Session):
    """
    Checks workspace for existing PDFs or documents (like Security Brochure_update Jul 2026.pdf)
    and automatically indexes them into ChromaDB and Database.
    """
    sample_files = [
        "Security Brochure_update Jul 2026.pdf",
        "Netwrix DSPM.pdf",
        "Netwrix Access Analyzer.pdf",
        "Certus Solution.pdf"
    ]

    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    
    for filename in sample_files:
        src_path = os.path.join(workspace_root, filename)
        dest_path = os.path.join(settings.UPLOAD_DIR, filename)

        if os.path.exists(src_path):
            if not os.path.exists(dest_path):
                shutil.copyfile(src_path, dest_path)
            target_path = dest_path
        elif os.path.exists(dest_path):
            target_path = dest_path
        else:
            # Create a placeholder sample document if not present
            continue

        # Parse and index
        try:
            pages = DocumentParserService.parse_pdf(target_path)
            if pages:
                sample_text = " ".join([p["text"] for p in pages[:3]])
                vendor, cat = DocumentParserService.detect_vendor_and_category(sample_text, filename)
                
                chunks = DocumentParserService.chunk_document(
                    pages_content=pages,
                    doc_name=filename,
                    vendor=vendor,
                    category=cat
                )
                
                vector_service.add_chunks(chunks)

                doc_rec = db.query(Document).filter(Document.document_name == filename).first()
                if not doc_rec:
                    doc_rec = Document(
                        document_name=filename,
                        file_path=target_path,
                        file_type="pdf",
                        vendor=vendor,
                        solution_category=cat,
                        page_count=len(pages),
                        chunk_count=len(chunks),
                        file_size_bytes=os.path.getsize(target_path),
                        status="indexed",
                        doc_metadata={"auto_imported": True}
                    )
                    db.add(doc_rec)
                    db.commit()
                print(f"Auto-imported and indexed {filename} ({len(pages)} pages, {len(chunks)} chunks).")
        except Exception as e:
            print(f"Notice auto-importing {filename}: {e}")
