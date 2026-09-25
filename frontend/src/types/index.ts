export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: 'admin' | 'user';
  is_active: boolean;
}

export interface DocumentItem {
  id: number;
  document_name: string;
  file_path: string;
  file_type: 'pdf' | 'docx' | 'pptx' | 'txt';
  vendor: string;
  solution_category: string;
  page_count: number;
  chunk_count: number;
  file_size_bytes: number;
  status: 'processing' | 'indexed' | 'failed';
  doc_metadata: Record<string, any>;
  created_date: string;
}

export interface SolutionItem {
  id: number;
  name: string;
  vendor: string;
  category: string;
  problem: string;
  description: string;
  features: string[];
  use_case: string[];
  competitor: string[];
  keywords: string[];
  discovery_questions: string[];
  documents: Array<{ document_name: string; pages?: number[] }>;
  created_at: string;
}

export interface ObjectionHandling {
  objection: string;
  answer: string;
}

export interface BattleCardItem {
  id: number;
  solution_id?: number;
  solution_name: string;
  vendor: string;
  category: string;
  overview: string;
  why_customer_needs: string;
  pain_points: string[];
  talking_points: string[];
  technical_advantages: string[];
  common_objections: ObjectionHandling[];
  target_buyer_personas: string[];
  created_at: string;
}

export interface SourceReference {
  document_name: string;
  page_number: number;
  snippet: string;
  vendor?: string;
  category?: string;
}

export interface DetectedSolution {
  id?: number;
  name: string;
  vendor: string;
  category: string;
  summary: string;
}

export interface ChatMessageItem {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  detected_solutions?: DetectedSolution[];
  sources?: SourceReference[];
  mode_applied?: string;
  timestamp: string;
  isLoading?: boolean;
}

export interface ConversationSummary {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationRecord extends ConversationSummary {
  messages: ChatMessageItem[];
}
