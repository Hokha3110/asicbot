import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Loader2, RefreshCw } from 'lucide-react';
import { ChatMessageItem } from '../../types';
import { ChatMessage } from './ChatMessage';

interface ChatWindowProps {
  messages: ChatMessageItem[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  onApplyPresalesMode: (mode: any, contextText: string) => void;
  isTransforming: boolean;
  onResetChat: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  isLoading,
  onApplyPresalesMode,
  isTransforming,
  onResetChat
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const samplePrompts = [
    'Khách hàng cần bảo vệ dữ liệu',
    'Tôi cần giải pháp kiểm tra hacker có vượt qua được hệ thống không',
    'Cần biết dữ liệu nhạy cảm nằm ở đâu',
    'Tư vấn giải pháp SOC & quản lý Log chi phí tối ưu'
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#070b09] relative overflow-hidden">
      {/* Top Bar */}
      <div className="px-4 sm:px-6 py-2 border-b border-emerald-950/80 bg-[#09110d]/50 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 text-slate-400 truncate">
          <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span className="truncate">AI Presales Assistant (Định dạng 8 phần chuẩn hóa)</span>
        </div>
        {messages.length > 0 && (
          <button
            onClick={onResetChat}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-900 hover:bg-emerald-950/80 text-slate-300 hover:text-emerald-300 border border-emerald-950 transition-colors shrink-0"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Chat mới</span>
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center p-6 text-center max-w-xl mx-auto">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-glow-jade mb-4">
              <Sparkles className="w-7 h-7" />
            </div>
            <h2 className="text-lg font-bold text-white mb-2">
              KALI0T
            </h2>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed">
              Trợ lý Presales thông minh. Tra cứu tài liệu PDF/DOCX/PPTX, tìm giải pháp theo nỗi đau khách hàng và tạo kịch bản tư vấn nhanh.
            </p>

            {/* Prompt Pills */}
            <div className="w-full space-y-2 text-left">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-emerald-500/80 mb-2">
                Gợi ý câu hỏi nhanh:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {samplePrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setInputText(prompt);
                      onSendMessage(prompt);
                    }}
                    className="p-3 rounded-xl glass-card text-xs text-slate-300 hover:text-emerald-300 text-left transition-all flex items-center justify-between group"
                  >
                    <span className="truncate mr-2">{prompt}</span>
                    <Send className="w-3.5 h-3.5 text-slate-500 group-hover:text-emerald-400 shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-emerald-950/40">
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                onApplyPresalesMode={onApplyPresalesMode}
                isTransforming={isTransforming}
              />
            ))}
            {isLoading && (
              <div className="py-5 px-4 sm:px-6 bg-[#0c1410]/50 border-y border-emerald-950/40">
                <div className="max-w-3xl mx-auto flex items-center gap-3 text-emerald-400 text-xs font-medium">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Kali0t đang truy vấn dữ liệu và tạo cấu trúc tư vấn Presales...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-3 sm:p-4 border-t border-emerald-950 bg-[#09110d]/90 backdrop-blur-md">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Nhập câu hỏi hoặc nhu cầu khách hàng (Shift+Enter để xuống dòng)..."
            rows={2}
            className="w-full bg-[#0d1612] border border-emerald-950 rounded-2xl px-4 py-3 pr-20 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500/80 transition-all resize-none shadow-inner"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="absolute right-2.5 bottom-3.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white text-xs font-bold flex items-center gap-1.5 shadow-glow-jade hover:from-emerald-500 hover:to-teal-500 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            <span className="hidden sm:inline">Gửi</span>
          </button>
        </form>
      </div>
    </div>
  );
};
