import React from 'react';
import { X, ShieldCheck, Tag, CheckCircle, HelpCircle, Swords, BookOpen, Layers } from 'lucide-react';
import { SolutionItem } from '../../types';

interface SolutionDetailModalProps {
  solution: SolutionItem | null;
  onClose: () => void;
  onOpenChatWithSolution: (solutionName: string) => void;
}

export const SolutionDetailModal: React.FC<SolutionDetailModalProps> = ({
  solution,
  onClose,
  onOpenChatWithSolution
}) => {
  if (!solution) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-[#0c1322] border border-slate-700/90 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 bg-[#111c33]/80 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-glow-cyan">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">{solution.name}</h3>
              <p className="text-xs text-cyan-400 font-medium">{solution.vendor} • <span className="text-slate-400">{solution.category}</span></p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs leading-relaxed text-slate-300">
          {/* Problem Solved */}
          <div>
            <h4 className="font-bold text-cyan-300 uppercase tracking-wider text-[11px] mb-1.5 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>Problem Solved (Vấn đề & Nỗi đau giải quyết)</span>
            </h4>
            <p className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 text-slate-200">
              {solution.problem}
            </p>
          </div>

          {/* Key Capabilities */}
          <div>
            <h4 className="font-bold text-emerald-300 uppercase tracking-wider text-[11px] mb-1.5 flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
              <span>Key Capabilities (Tính năng nổi bật)</span>
            </h4>
            <ul className="space-y-1 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              {(solution.features || []).map((feat, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">▹</span>
                  <span>{feat}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Use Cases */}
          <div>
            <h4 className="font-bold text-violet-300 uppercase tracking-wider text-[11px] mb-1.5 flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5 text-violet-400" />
              <span>Use Cases (Tình huống ứng dụng)</span>
            </h4>
            <ul className="space-y-1 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              {(solution.use_case || []).map((uc, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-violet-400 font-bold">▹</span>
                  <span>{uc}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Customer Discovery Questions */}
          <div>
            <h4 className="font-bold text-amber-300 uppercase tracking-wider text-[11px] mb-1.5 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
              <span>Customer Discovery Questions (Câu hỏi khai thác Presales)</span>
            </h4>
            <ol className="space-y-1 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              {(solution.discovery_questions || []).map((q, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-amber-400 font-bold">{idx + 1}.</span>
                  <span>{q}</span>
                </li>
              ))}
            </ol>
          </div>

          {/* Competitors & Keywords */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-bold text-rose-300 uppercase tracking-wider text-[11px] mb-1.5 flex items-center gap-1.5">
                <Swords className="w-3.5 h-3.5 text-rose-400" />
                <span>Competitors / Alternatives</span>
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {(solution.competitor || []).map((comp, idx) => (
                  <span key={idx} className="px-2 py-1 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 text-[10px]">
                    {comp}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[11px] mb-1.5 flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-slate-400" />
                <span>Keywords</span>
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {(solution.keywords || []).map((kw, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono text-[10px] border border-slate-700">
                    #{kw}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-[#111c33]/60 flex items-center justify-between shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
          >
            Đóng
          </button>
          <button
            onClick={() => {
              onClose();
              onOpenChatWithSolution(solution.name);
            }}
            className="px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-xs font-bold text-white shadow-glow-cyan hover:from-cyan-400 hover:to-blue-500 transition-all flex items-center gap-2"
          >
            <span>Tư vấn giải pháp này với AI</span>
          </button>
        </div>
      </div>
    </div>
  );
};
