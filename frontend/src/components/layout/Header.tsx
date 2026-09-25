import React from 'react';
import { Cpu, Activity, BookOpen, Menu, Sparkles } from 'lucide-react';

interface HeaderProps {
  llmProvider: string;
  setLlmProvider: (p: string) => void;
  indexedDocsCount: number;
  solutionsCount: number;
  onOpenMobileSidebar: () => void;
  onToggleMobileRightPanel?: () => void;
  activeTab?: string;
}

export const Header: React.FC<HeaderProps> = ({
  llmProvider,
  setLlmProvider,
  indexedDocsCount,
  solutionsCount,
  onOpenMobileSidebar,
  onToggleMobileRightPanel,
  activeTab
}) => {
  return (
    <header className="h-14 min-w-0 shrink-0 border-b border-emerald-950/80 bg-[#09110d]/90 backdrop-blur-md px-3 sm:px-6 flex items-center justify-between z-30">
      {/* Left side: Hamburger & Knowledge Stats */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="p-1.5 rounded-lg bg-surface-800 text-slate-300 hover:text-white md:hidden"
          title="Mở Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden lg:flex items-center gap-3 text-xs min-w-0">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-900 border border-emerald-950 whitespace-nowrap">
            <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400">Knowledge:</span>
            <span className="font-mono text-emerald-300 font-bold">{indexedDocsCount} docs</span>
          </div>
          
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-900 border border-emerald-950 whitespace-nowrap">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400">Catalog:</span>
            <span className="font-mono text-emerald-300 font-bold">{solutionsCount} solutions</span>
          </div>
        </div>

        <div className="block lg:hidden min-w-0">
          <span className="font-bold text-xs text-white">KALI0T</span>
        </div>
      </div>

      {/* Right side: AI Selector & Mobile Toggle */}
      <div className="flex items-center gap-2 min-w-0">
        <div className="flex items-center gap-1.5 text-xs min-w-0">
          <select
            value={llmProvider}
            onChange={(e) => setLlmProvider(e.target.value)}
            className="max-w-[min(42vw,15rem)] bg-[#0b1612] text-xs font-mono text-emerald-300 border border-emerald-900/60 rounded-lg px-2.5 py-1 focus:outline-none focus:border-emerald-500 cursor-pointer"
          >
            <option value="gemini">✨ Google Gemini 2.5 Flash</option>
            <option value="openai">OpenAI GPT-4o</option>
            <option value="ollama">Ollama Local LLM</option>
            <option value="mock">Offline Native Engine</option>
          </select>
        </div>

        {activeTab === 'chat' && onToggleMobileRightPanel && (
          <button
            onClick={onToggleMobileRightPanel}
            className="px-2 py-1 rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-800/60 md:hidden flex items-center gap-1 text-xs font-semibold"
          >
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Modes</span>
          </button>
        )}
      </div>
    </header>
  );
};
