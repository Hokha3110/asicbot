import React, { useState } from 'react';
import { Search, Sparkles, Loader2 } from 'lucide-react';
import { SolutionItem } from '../../types';
import { api } from '../../services/api';

interface SmartSearchProps {
  onResults: (results: SolutionItem[]) => void;
  onClear: () => void;
}

export const SmartSearch: React.FC<SmartSearchProps> = ({ onResults, onClear }) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const smartExamples = [
    'Khách hàng cần kiểm tra hacker có vượt qua hệ thống không',
    'Cần biết dữ liệu nhạy cảm nằm ở đâu trên Cloud và On-premise',
    'Quản trị đặc quyền Active Directory theo Least Privilege'
  ];

  const handleSmartSearch = async (searchTerm: string) => {
    if (!searchTerm.trim()) return;
    setIsSearching(true);
    try {
      const data = await api.smartSearch(searchTerm);
      onResults(data);
    } catch (err) {
      console.error('Smart search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="glass-panel-glow rounded-2xl p-4 sm:p-5 mb-3 border-emerald-950">
      <div className="flex items-center gap-2 mb-1.5">
        <Sparkles className="w-4 h-4 text-emerald-400" />
        <h3 className="text-xs sm:text-sm font-bold text-white uppercase tracking-wider">
          Smart NLP Intent Search (Tìm theo nhu cầu tự nhiên)
        </h3>
      </div>
      <p className="text-xs text-slate-400 mb-3">
        Nhập câu hỏi hoặc mô tả nỗi đau của khách hàng để AI tự động tìm giải pháp phù hợp nhất.
      </p>

      {/* Input Bar */}
      <div className="flex items-center gap-2 mb-3 min-w-0">
        <div className="relative flex-1 min-w-0">
          <Search className="w-4 h-4 absolute left-3 top-3 text-emerald-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSmartSearch(query)}
            placeholder="VD: Kiểm tra tường lửa có chặn được ransomware mới không..."
            className="w-full bg-[#0b1612] border border-emerald-950 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
        <button
          onClick={() => handleSmartSearch(query)}
          disabled={!query.trim() || isSearching}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-xs font-bold text-white shadow-glow-jade hover:from-emerald-500 hover:to-teal-500 flex items-center gap-1.5 shrink-0 disabled:opacity-50"
        >
          {isSearching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
          <span>Tìm</span>
        </button>
        {query && (
          <button
            onClick={() => {
              setQuery('');
              onClear();
            }}
            className="px-3 py-2 rounded-xl bg-surface-900 hover:bg-emerald-950 text-xs font-semibold text-slate-300"
          >
            Reset
          </button>
        )}
      </div>

      {/* Quick Example Pills */}
      <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
        <span className="text-slate-500 mr-1">Gợi ý:</span>
        {smartExamples.map((ex, idx) => (
          <button
            key={idx}
            onClick={() => {
              setQuery(ex);
              handleSmartSearch(ex);
            }}
            className="px-2.5 py-1 rounded-lg bg-surface-900 hover:bg-emerald-950 text-slate-300 hover:text-emerald-300 border border-emerald-950 transition-all text-left truncate max-w-xs"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  );
};
