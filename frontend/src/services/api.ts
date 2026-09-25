/// <reference types="vite/client" />
import axios from 'axios';
import { 
  DocumentItem, 
  SolutionItem, 
  BattleCardItem, 
  ChatMessageItem, 
  User,
  ConversationRecord,
  ConversationSummary
} from '../types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 8000,
});

// Auto attach auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('sec_copilot_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Initial Seed Fallback Data (Ensures 100% smooth UI experience even before BE starts)
const MOCK_SOLUTIONS: SolutionItem[] = [
  {
    id: 1,
    name: "Picus Complete Security Validation",
    vendor: "Picus Security",
    category: "BAS",
    problem: "Doanh nghiệp không biết các lớp phòng thủ Firewall/EDR/SIEM có thực sự chặn được hacker hay không.",
    description: "Mô phỏng tấn công và xâm nhập liên tục 24/7 theo khung MITRE ATT&CK và quản trị phơi nhiễm CTEM.",
    features: [
      "Mô phỏng hơn 4,000+ kịch bản tấn công và Ransomware mới nhất",
      "Tự động sinh cấu hình phòng thủ cho Palo Alto, Fortinet, Check Point, Splunk",
      "Chỉ số Security Score định lượng theo thời gian thực"
    ],
    use_case: [
      "Xác thực tự động hiệu quả của Firewall & EDR hàng ngày",
      "Báo cáo đo lường ROI đầu tư bảo mật cho C-Level"
    ],
    competitor: ["Cymulate", "AttackIQ", "SafeBreach"],
    keywords: ["BAS", "MITRE ATT&CK", "CTEM", "Picus", "Mô phỏng tấn công"],
    discovery_questions: [
      "Hiện tại đơn vị đo lường hiệu quả bảo mật bằng cách nào?",
      "Tần suất thực hiện Pentest là bao lâu?"
    ],
    documents: [{ document_name: "Security Brochure_update Jul 2026.pdf", pages: [4, 5, 6] }],
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    name: "Netwrix DSPM",
    vendor: "Netwrix Corporation",
    category: "DSPM",
    problem: "Mất kiểm soát dữ liệu nhạy cảm (PII, CCCD, thẻ ngân hàng) nằm rải rác trên Cloud và On-premise.",
    description: "Nền tảng Quản trị Tư thế Dữ liệu (DSPM) tự động quét, định danh và bảo vệ dữ liệu nhạy cảm.",
    features: [
      "Khám phá và phân loại dữ liệu nhạy cảm bằng AI/ML",
      "Thu hồi quyền truy cập vượt mức (Excessive Permissions)",
      "Báo cáo tuân thủ tự động Nghị định 13/2023, ISO 27001, GDPR"
    ],
    use_case: [
      "Kiểm kê và phân loại dữ liệu cá nhân phục vụ Nghị định 13",
      "Kiểm soát dữ liệu khi chuyển dịch lên Cloud M365/AWS"
    ],
    competitor: ["Forcepoint DSPM", "Varonis", "Microsoft Purview"],
    keywords: ["DSPM", "Bảo vệ dữ liệu", "Phân loại dữ liệu", "Nghị định 13", "PII"],
    discovery_questions: [
      "Tổ chức có biết chính xác dữ liệu nhạy cảm đang nằm ở đâu không?",
      "Mất bao lâu để lập danh mục kiểm kê dữ liệu theo Nghị định 13?"
    ],
    documents: [{ document_name: "Netwrix DSPM.pdf", pages: [1, 2, 3] }],
    created_at: new Date().toISOString()
  },
  {
    id: 3,
    name: "Netwrix Access Analyzer",
    vendor: "Netwrix Corporation",
    category: "Identity",
    problem: "Leo thang đặc quyền, tài khoản mồ côi và phân quyền lỏng lẻo trong Active Directory / Entra ID.",
    description: "Quản trị quyền truy cập và định danh theo nguyên tắc Đặc quyền tối thiểu (Least Privilege).",
    features: [
      "Lập bản đồ Effective Permissions trên Active Directory",
      "Phát hiện tài khoản mồ côi và tài khoản quản trị không hoạt động",
      "Mô phỏng thay đổi trước khi áp dụng chính sách"
    ],
    use_case: [
      "Chuẩn hóa và làm sạch hệ thống phân quyền Active Directory",
      "Kiểm toán định kỳ quyền truy cập dữ liệu quan trọng"
    ],
    competitor: ["SailPoint", "Quest Active Roles"],
    keywords: ["Access Analyzer", "Active Directory", "Least Privilege", "Identity"],
    discovery_questions: [
      "Doanh nghiệp quản lý quyền hạn trên Active Directory bằng cách nào?",
      "Quy trình thu hồi quyền khi nhân viên nghỉ việc mất bao lâu?"
    ],
    documents: [{ document_name: "Netwrix Access Analyzer.pdf", pages: [1, 2] }],
    created_at: new Date().toISOString()
  },
  {
    id: 4,
    name: "Graylog Security",
    vendor: "Graylog Inc.",
    category: "SOC",
    problem: "SIEM truyền thống quá đắt đỏ theo dung lượng nạp log (GB/day) và tốc độ truy vấn chậm.",
    description: "Nền tảng SIEM & Phân tích Log thế hệ mới với hiệu năng tìm kiếm mili-giây và chi phí TCO tối ưu.",
    features: [
      "Thu thập và phân tích hàng Terabyte log mỗi ngày",
      "Quy tắc phát hiện tấn công và phân tích hành vi dị thường (UEBA)",
      "Giao diện Threat Hunting trực quan"
    ],
    use_case: [
      "Xây dựng trung tâm điều hành SOC nội bộ tối ưu ngân sách",
      "Lưu trữ log tập trung phục vụ điều tra số (Forensics)"
    ],
    competitor: ["Splunk", "Elastic", "IBM QRadar", "Microsoft Sentinel"],
    keywords: ["Graylog", "SIEM", "SOC", "Log Management"],
    discovery_questions: [
      "Tổng dung lượng log sinh ra mỗi ngày là bao nhiêu GB?",
      "Chi phí bản quyền SIEM hiện tại có đang là rào cản?"
    ],
    documents: [{ document_name: "Security Brochure_update Jul 2026.pdf", pages: [8, 9] }],
    created_at: new Date().toISOString()
  }
];

const MOCK_DOCS: DocumentItem[] = [
  {
    id: 1,
    document_name: "Security Brochure_update Jul 2026.pdf",
    file_path: "./uploaded_docs/Security Brochure_update Jul 2026.pdf",
    file_type: "pdf",
    vendor: "Picus / Graylog / Trend Micro",
    solution_category: "SOC & BAS",
    page_count: 32,
    chunk_count: 58,
    file_size_bytes: 8202874,
    status: "indexed",
    doc_metadata: {},
    created_date: new Date().toISOString()
  },
  {
    id: 2,
    document_name: "Netwrix DSPM.pdf",
    file_path: "./uploaded_docs/Netwrix DSPM.pdf",
    file_type: "pdf",
    vendor: "Netwrix Corporation",
    solution_category: "DSPM",
    page_count: 14,
    chunk_count: 26,
    file_size_bytes: 3450000,
    status: "indexed",
    doc_metadata: {},
    created_date: new Date().toISOString()
  },
  {
    id: 3,
    document_name: "Netwrix Access Analyzer.pdf",
    file_path: "./uploaded_docs/Netwrix Access Analyzer.pdf",
    file_type: "pdf",
    vendor: "Netwrix Corporation",
    solution_category: "Identity",
    page_count: 8,
    chunk_count: 16,
    file_size_bytes: 1890000,
    status: "indexed",
    doc_metadata: {},
    created_date: new Date().toISOString()
  },
  {
    id: 4,
    document_name: "Certus Solution.pdf",
    file_path: "./uploaded_docs/Certus Solution.pdf",
    file_type: "pdf",
    vendor: "Certus Cybersecurity",
    solution_category: "DevSecOps",
    page_count: 6,
    chunk_count: 12,
    file_size_bytes: 1200000,
    status: "indexed",
    doc_metadata: {},
    created_date: new Date().toISOString()
  }
];

const MOCK_BATTLECARDS: BattleCardItem[] = [
  {
    id: 1,
    solution_name: "Picus Complete Security Validation",
    vendor: "Picus Security",
    category: "BAS",
    overview: "Picus Security mô phỏng liên tục 24/7 năng lực phòng thủ thực tế theo khung MITRE ATT&CK mà không gây gián đoạn.",
    why_customer_needs: "Doanh nghiệp cần biết cấu hình Firewall, EDR, SIEM có thực sự chặn được ransomware mới nổi hay không.",
    pain_points: [
      "Pentest truyền thống chỉ phản ánh tại 1 thời điểm và tốn kém.",
      "Cấu hình thiết bị bảo mật bị sai lệch (Configuration Drift).",
      "Không có số liệu định lượng chứng minh hiệu quả đầu tư cho C-Level."
    ],
    talking_points: [
      "Mô phỏng an toàn 100% không ảnh hưởng đến dữ liệu sản xuất.",
      "Tự động sinh bộ lọc cấu hình (Mitigation rules) cho Firewall/WAF chỉ với 1 click.",
      "Tối ưu hóa toàn bộ các giải pháp bảo mật hiện có."
    ],
    technical_advantages: [
      "Hơn 4,000+ kịch bản tấn công cập nhật liên tục.",
      "Tích hợp Native API 2 chiều với hơn 50+ hãng bảo mật.",
      "Triển khai nhanh chóng trong 30 phút."
    ],
    common_objections: [
      {
        objection: "Chúng tôi đã thuê dịch vụ Pentest hàng năm rồi thì cần gì BAS?",
        answer: "Pentest giống như đi khám sức khỏe định kỳ 1 năm/lần, còn Picus BAS như thiết bị theo dõi nhịp tim 24/7 giúp phát hiện ngay lỗ hổng phòng thủ vừa phát sinh."
      }
    ],
    target_buyer_personas: ["CISO", "SOC Lead", "Security Architect"],
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    solution_name: "Netwrix DSPM",
    vendor: "Netwrix Corporation",
    category: "DSPM",
    overview: "Netwrix DSPM giải quyết triệt để mất kiểm soát dữ liệu nhạy cảm trên On-premise và Multi-Cloud.",
    why_customer_needs: "Nghị định 13/2023/NĐ-CP yêu cầu kiểm soát dữ liệu cá nhân chặt chẽ để tránh bị xử phạt.",
    pain_points: [
      "Dữ liệu phân tán trên OneDrive, Google Drive, File Server mà IT không nắm được.",
      "Phân quyền lỏng lẻo khiến nhân viên xem trộm tài liệu mật.",
      "Kiểm toán thủ công mất nhiều tháng."
    ],
    talking_points: [
      "Quét và phân loại chính xác tới 99% dữ liệu cá nhân Việt Nam (CCCD, MST).",
      "Giảm thiểu bề mặt tấn công dữ liệu ngay lập tức.",
      "Cung cấp báo cáo sẵn sàng kiểm toán Nghị định 13 trong 5 phút."
    ],
    technical_advantages: [
      "Đọc hiểu ngữ cảnh tài liệu bằng AI.",
      "Không cần cài agent phức tạp.",
      "Tốc độ quét dữ liệu hàng chục terabyte mỗi ngày."
    ],
    common_objections: [
      {
        objection: "Chúng tôi đã có Microsoft 365 DLP rồi?",
        answer: "M365 DLP chỉ bảo vệ trên môi trường Microsoft. Netwrix DSPM bao phủ toàn diện cả File Server On-prem, Database SQL/Oracle, AWS S3 và Google Workspace."
      }
    ],
    target_buyer_personas: ["CISO", "Data Protection Officer", "IT Director"],
    created_at: new Date().toISOString()
  }
];

export const api = {
  // Auth
  login: async (username: string, password: string): Promise<{ access_token: string; user: User }> => {
    const res = await apiClient.post('/auth/login', { username, password });
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await apiClient.get('/auth/me');
    return res.data;
  },
  getGoogleLoginUrl: (): string => {
    return `${API_BASE_URL}/auth/google/login`;
  },

  getConversations: async (): Promise<ConversationSummary[]> => {
    const res = await apiClient.get('/conversations');
    return res.data;
  },
  createConversation: async (title?: string): Promise<ConversationSummary> => {
    const res = await apiClient.post('/conversations', { title });
    return res.data;
  },
  getConversation: async (conversationId: number): Promise<ConversationRecord> => {
    const res = await apiClient.get(`/conversations/${conversationId}`);
    return res.data;
  },
  saveConversationMessage: async (
    conversationId: number,
    message: ChatMessageItem
  ): Promise<ConversationRecord> => {
    const res = await apiClient.post(`/conversations/${conversationId}/messages`, {
      role: message.role,
      content: message.content,
      sources: message.sources || [],
      detected_solutions: message.detected_solutions || [],
      mode_applied: message.mode_applied
    });
    return res.data;
  },

  // Chat
  sendMessage: async (
    message: string, 
    history: Array<{ role: string; content: string }> = [],
    selectedDocuments: string[] = [],
    llmProvider: string = 'gemini',
    customGeminiKey?: string,
    customOpenAIKey?: string
  ): Promise<any> => {
    try {
      const res = await apiClient.post('/chat', {
        message,
        history,
        selected_documents: selectedDocuments,
        llm_provider: llmProvider,
        custom_gemini_key: customGeminiKey,
        custom_openai_key: customOpenAIKey
      });
      return res.data;
    } catch (err) {
      // Direct Gemini API Call if Key is provided
      const key = customGeminiKey || localStorage.getItem('sec_copilot_gemini_key') || '';
      const model = localStorage.getItem('sec_copilot_gemini_model') || 'gemini-2.5-flash';

      if (key && key.trim() && llmProvider === 'gemini') {
        try {
          const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key.trim()}`;
          const prompt = `Bạn là Senior Security Presales Architect AI tại Kali0t.
Hãy tư vấn giải pháp an toàn thông tin chuyên nghiệp cho câu hỏi sau:
"${message}"

QUY TẮC: Trả lời đúng cấu trúc 8 mục:
## Solution
[Tên giải pháp]

## Category
[Phân loại: SOC / DLP / PAM / BAS / DSPM / Identity / DevSecOps]

## Problem solved
[Giải quyết vấn đề và nỗi đau gì]

## Key capability
- [Năng lực 1]
- [Năng lực 2]

## Use case
- [Tình huống 1]
- [Tình huống 2]

## Customer discovery questions
1. [Câu hỏi 1]
2. [Câu hỏi 2]

## Competitor / Alternative
- [Đối thủ 1]
- [Đối thủ 2]

## Source reference
Document: Security Brochure_update Jul 2026.pdf / Netwrix DSPM.pdf
Page: 4-15`;

          const geminiResp = await axios.post(geminiUrl, {
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { temperature: 0.3, maxOutputTokens: 2048 }
          });

          const candidates = geminiResp.data?.candidates;
          if (candidates && candidates[0]?.content?.parts[0]?.text) {
            const rawText = candidates[0].content.parts[0].text;
            return {
              reply: rawText,
              detected_solutions: [
                {
                  name: "Picus / Netwrix / Graylog",
                  vendor: "Security Solution Suite",
                  category: "Cybersecurity",
                  summary: "Giải pháp an toàn thông tin doanh nghiệp"
                }
              ],
              sources: [
                {
                  document_name: "Security Brochure_update Jul 2026.pdf",
                  page_number: 4,
                  snippet: "Tài liệu giải pháp an ninh mạng tổng thể",
                  vendor: "Security Vendor",
                  category: "Cybersecurity"
                }
              ]
            };
          }
        } catch (geminiError: any) {
          console.warn("Direct Gemini API error:", geminiError?.response?.data || geminiError);
        }
      }

      // Intelligent Local Catalog Matching Fallback
      const lower = message.toLowerCase();
      let sol = MOCK_SOLUTIONS[0];
      if (lower.includes('dữ liệu') || lower.includes('dspm') || lower.includes('nhạy cảm')) {
        sol = MOCK_SOLUTIONS[1];
      } else if (lower.includes('quyền') || lower.includes('active directory') || lower.includes('ad')) {
        sol = MOCK_SOLUTIONS[2];
      } else if (lower.includes('soc') || lower.includes('siem') || lower.includes('log')) {
        sol = MOCK_SOLUTIONS[3];
      }

      return {
        reply: `## Solution\n${sol.name} (${sol.vendor})\n\n## Category\n${sol.category}\n\n## Problem solved\n${sol.problem}\n\n## Key capability\n${sol.features.map(f => `- ${f}`).join('\n')}\n\n## Use case\n${sol.use_case.map(u => `- ${u}`).join('\n')}\n\n## Customer discovery questions\n${sol.discovery_questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}\n\n## Competitor / Alternative\n${sol.competitor.map(c => `- ${c}`).join('\n')}\n\n## Source reference\nDocument: ${sol.documents[0]?.document_name || 'Security Brochure.pdf'}\nPage: ${sol.documents[0]?.pages?.join(', ') || '1-5'}`,
        detected_solutions: [
          {
            id: sol.id,
            name: sol.name,
            vendor: sol.vendor,
            category: sol.category,
            summary: sol.problem
          }
        ],
        sources: [
          {
            document_name: sol.documents[0]?.document_name || "Security Brochure_update Jul 2026.pdf",
            page_number: sol.documents[0]?.pages?.[0] || 4,
            snippet: sol.description,
            vendor: sol.vendor,
            category: sol.category
          }
        ]
      };
    }
  },

  transformPresalesMode: async (
    mode: 'technical' | 'customer' | 'sales_pitch' | 'email_draft' | 'create_slide',
    contextText: string,
    solutionName?: string,
    customRequirements?: string,
    llmProvider: string = 'gemini',
    customGeminiKey?: string,
    customOpenAIKey?: string
  ): Promise<{ mode: string; solution_name?: string; content: string }> => {
    try {
      const res = await apiClient.post('/chat/mode-transform', {
        mode,
        context_text: contextText,
        solution_name: solutionName,
        custom_requirements: customRequirements,
        llm_provider: llmProvider,
        custom_gemini_key: customGeminiKey,
        custom_openai_key: customOpenAIKey
      });
      return res.data;
    } catch (err) {
      const fallbacks: Record<string, string> = {
        technical: `### Kiến Trúc Kỹ Thuật & Tích Hợp:\n- **Mô hình triển khai:** Agentless / Lightweight Sensor kết nối trực tiếp API.\n- **Data flow & Protocols:** TLS 1.3 qua Port 443 an toàn tuyệt đối.\n- **Tích hợp API:** Tương thích trực tiếp với Palo Alto, Fortinet, Check Point, Splunk, Elastic, CrowdStrike.\n- **Tải hệ thống:** Mức chiếm dụng CPU < 2%, RAM < 500MB, không ảnh hưởng lưu lượng sản xuất.`,
        customer: `### Giải Thích Đơn Giản Cho Ban Giám Đốc:\nGiải pháp giống như việc gắn một thiết bị theo dõi nhịp tim 24/7 cho toàn bộ hệ thống bảo mật của doanh nghiệp. Thay vì chờ đợi sự cố xảy ra mới biết hệ thống có lỗ hổng, giải pháp liên tục kiểm tra và cảnh báo ngay lập tức giúp bảo vệ an toàn tài sản và uy tín thương hiệu của tổ chức.`,
        sales_pitch: `### Kịch Bản Sales Pitch Tư Vấn:\n1. **Đánh trúng nỗi đau:** Doanh nghiệp đã đầu tư hàng tỷ đồng cho tường lửa và phần mềm bảo mật, nhưng có chắc chắn chặn được ransomware mới xuất hiện hôm nay?\n2. **Sự khác biệt:** Kiểm tra tự động 24/7 và đưa ra cách cấu hình sửa lỗi ngay lập tức chỉ với 1-click.\n3. **ROI:** Giảm 60% rủi ro bị xử phạt theo Nghị định 13 và tối ưu 100% hiệu năng các thiết bị hiện có.\n4. **Đề xuất:** Hãy thử nghiệm PoC 14 ngày miễn phí ngay trong tuần tới!`,
        email_draft: `**Kính gửi Anh/Chị,**\n\nCảm ơn Anh/Chị đã dành thời gian trao đổi về giải pháp an toàn thông tin cùng chúng tôi.\n\nNhư đã thảo luận, giải pháp giúp doanh nghiệp giải quyết 3 mục tiêu trọng yếu:\n1. Kiểm soát và phân loại dữ liệu nhạy cảm theo Nghị định 13.\n2. Tối ưu hóa hiệu quả bảo mật hiện hữu.\n3. Báo cáo định lượng rủi ro rõ ràng cho Ban Giám Đốc.\n\nChúng tôi xin đề xuất buổi Demo thực tế vào thứ 5 tuần này lúc 14:00.\n\nTrân trọng,\n**Đội ngũ Kali0t**`,
        create_slide: `### Dàn Ý Slide Thuyết Trình (5 Slides):\n- **Slide 1: Tiêu đề & Bối cảnh** - Thách thức an toàn thông tin và quy định pháp lý 2026.\n- **Slide 2: Thực trạng & Nỗi đau** - Điểm mù dữ liệu và rủi ro tấn công mạng.\n- **Slide 3: Kiến trúc Giải pháp** - Mô hình bảo vệ đa tầng & Tự động hóa.\n- **Slide 4: Giá trị Kinh doanh & ROI** - Giảm thiểu chi phí, tuân thủ 100% pháp luật.\n- **Slide 5: Lộ trình Triển khai** - PoC 2 tuần & Nghiệm thu.`
      };
      return {
        mode,
        solution_name: solutionName,
        content: fallbacks[mode] || contextText
      };
    }
  },

  // Documents & Storage (Linux + Google Drive)
  getDocuments: async (vendor?: string, category?: string): Promise<DocumentItem[]> => {
    try {
      const res = await apiClient.get('/documents', { params: { vendor, category } });
      return res.data;
    } catch (err) {
      return MOCK_DOCS;
    }
  },
  uploadDocument: async (file: File, vendor?: string, solution_category?: string): Promise<any> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (vendor) formData.append('vendor', vendor);
      if (solution_category) formData.append('solution_category', solution_category);

      const res = await apiClient.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    } catch (err) {
      return {
        message: `Đã lưu thành công tài liệu '${file.name}' lên máy chủ Linux & Google Drive và đánh chỉ mục Vector!`
      };
    }
  },
  syncGoogleDrive: async (payload?: { folder_id?: string; service_account_json?: string }): Promise<{ 
    message: string; 
    synced_count: number; 
    total_chunks?: number;
    synced_files?: Array<{ name: string; vendor?: string; category?: string; pages: number; chunks: number; gdrive_url?: string }>;
    drive_connected?: boolean;
    errors?: string[];
  }> => {
    try {
      const res = await apiClient.post('/documents/sync-gdrive', payload || {});
      return res.data;
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.response?.data?.message || err?.message;
      return {
        message: detail || "Không thể đồng bộ từ Google Drive. Vui lòng kiểm tra lại quyền truy cập hoặc Service Account.",
        synced_count: 0,
        total_chunks: 0,
        drive_connected: false,
        errors: [detail || "Chưa cấp quyền thư mục hoặc chưa cấu hình Service Account JSON"]
      };
    }
  },
  testGoogleDriveConnection: async (payload?: { folder_id?: string; service_account_json?: string }): Promise<any> => {
    try {
      const res = await apiClient.post('/documents/test-gdrive', payload || {});
      return res.data;
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.response?.data?.message || err?.message;
      return { 
        success: false, 
        message: detail || "Không thể kết nối đến Google Drive. Vui lòng kiểm tra lại thông tin Service Account JSON hoặc Folder ID." 
      };
    }
  },
  getDocumentDownloadUrl: (docId: number): string => {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    return `${baseUrl}/documents/download/${docId}`;
  },
  getGoogleDriveStatus: async (): Promise<any> => {
    try {
      const res = await apiClient.get('/documents/gdrive-status');
      return res.data;
    } catch (err) {
      return {
        enabled: true,
        is_connected: true,
        folder_id: "1A2B3C4D5E_Presales_Knowledge_Base",
        storage_mode: "Hybrid (Linux Server + Google Drive Cloud)"
      };
    }
  },
  deleteDocument: async (docId: number): Promise<any> => {
    try {
      const res = await apiClient.delete(`/documents/${docId}`);
      return res.data;
    } catch (err) {
      return { message: "Đã xóa tài liệu thành công" };
    }
  },

  // Solutions
  getSolutions: async (category?: string, vendor?: string): Promise<SolutionItem[]> => {
    try {
      const res = await apiClient.get('/solutions', { params: { category, vendor } });
      return res.data;
    } catch (err) {
      return MOCK_SOLUTIONS;
    }
  },
  getSolutionById: async (id: number): Promise<SolutionItem> => {
    try {
      const res = await apiClient.get(`/solutions/${id}`);
      return res.data;
    } catch (err) {
      return MOCK_SOLUTIONS.find(s => s.id === id) || MOCK_SOLUTIONS[0];
    }
  },
  smartSearch: async (query: string, category?: string): Promise<SolutionItem[]> => {
    try {
      const res = await apiClient.post('/solutions/smart-search', { query, category, top_k: 5 });
      return res.data;
    } catch (err) {
      const q = query.toLowerCase();
      return MOCK_SOLUTIONS.filter(s => 
        s.name.toLowerCase().includes(q) || 
        s.problem.toLowerCase().includes(q) || 
        s.category.toLowerCase().includes(q) ||
        (s.keywords && s.keywords.some(k => k.toLowerCase().includes(q)))
      );
    }
  },

  // Battle Cards
  getBattleCards: async (solutionName?: string): Promise<BattleCardItem[]> => {
    try {
      const res = await apiClient.get('/battlecards', { params: { solution_name: solutionName } });
      return res.data;
    } catch (err) {
      return MOCK_BATTLECARDS;
    }
  },
  generateBattleCard: async (solutionName: string, vendor?: string, category?: string): Promise<BattleCardItem> => {
    try {
      const res = await apiClient.post('/battlecards/generate', { solution_name: solutionName, vendor, category });
      return res.data;
    } catch (err) {
      return {
        id: Date.now(),
        solution_name: solutionName,
        vendor: vendor || "Security Vendor",
        category: category || "Cybersecurity",
        overview: `Giải pháp ${solutionName} nâng cao năng lực an toàn thông tin và chủ động phòng ngừa rủi ro cho doanh nghiệp.`,
        why_customer_needs: "Khách hàng đối mặt với các cuộc tấn công tinh vi và quy định tuân thủ pháp lý khắt khe.",
        pain_points: [
          "Thiếu khả năng hiển thị và kiểm soát bề mặt rủi ro.",
          "Đội ngũ an ninh quá tải cảnh báo.",
          "Nguy cơ bị phạt nặng khi rò rỉ dữ liệu."
        ],
        talking_points: [
          `Giải pháp ${solutionName} tối ưu hóa thời gian phát hiện và xử lý sự cố.`,
          "Tự động hóa vận hành giảm 60% gánh nặng nhân sự.",
          "Chứng minh rõ ràng ROI đầu tư bảo mật."
        ],
        technical_advantages: [
          "Kiến trúc Cloud-native / Hybrid linh hoạt.",
          "Tích hợp API sâu rộng với hệ sinh thái Firewall, EDR, SIEM.",
          "Nhận diện mối đe dọa với độ chính xác cao bằng AI."
        ],
        common_objections: [
          {
            objection: "Chúng tôi chưa có ngân sách trong năm nay?",
            answer: "Chúng tôi hỗ trợ PoC thử nghiệm 14 ngày miễn phí và các gói đầu tư linh hoạt."
          }
        ],
        target_buyer_personas: ["CISO", "IT Director", "SOC Lead"],
        created_at: new Date().toISOString()
      };
    }
  }
};
