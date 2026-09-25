import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User as UserIcon, Copy, Check } from 'lucide-react';
import { ChatMessageItem } from '../../types';
import { SourceBadge } from './SourceBadge';
import { PresalesActions } from './PresalesActions';

interface ChatMessageProps {
  message: ChatMessageItem;
  onApplyPresalesMode: (mode: any, contextText: string) => void;
  isTransforming: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onApplyPresalesMode,
  isTransforming
}) => {
  const [copied, setCopied] = React.useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`py-4 px-4 sm:px-6 transition-colors ${
      isUser ? 'bg-[#09110d]/40' : 'bg-[#0d1612]/30'
    }`}>
      <div className="max-w-3xl mx-auto flex items-start gap-3.5">
        {/* Avatar */}
        <div className="shrink-0 mt-0.5">
          {isUser ? (
            <div className="w-7 h-7 rounded-lg bg-surface-800 border border-emerald-950 flex items-center justify-center text-slate-400">
              <UserIcon className="w-3.5 h-3.5" />
            </div>
          ) : (
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-glow-jade">
              <Bot className="w-3.5 h-3.5" />
            </div>
          )}
        </div>

        {/* Message Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-200">
                {isUser ? 'Presales Engineer' : 'Kali0t'}
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {message.timestamp}
              </span>
              {message.mode_applied && (
                <span className="text-[10px] px-2 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                  {message.mode_applied}
                </span>
              )}
            </div>

            {!isUser && (
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-emerald-300 transition-colors p-1 rounded hover:bg-surface-800"
                title="Sao chép"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Đã chép' : 'Chép'}</span>
              </button>
            )}
          </div>

          {/* Body */}
          <div className="presales-prose text-xs sm:text-sm text-slate-200 leading-relaxed font-sans break-words">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>

          {/* Sources Badge */}
          {!isUser && message.sources && (
            <SourceBadge sources={message.sources} />
          )}

          {/* Presales Actions */}
          {!isUser && (
            <PresalesActions
              onSelectMode={(mode) => onApplyPresalesMode(mode, message.content)}
              disabled={isTransforming}
            />
          )}
        </div>
      </div>
    </div>
  );
};
