import React from 'react';
import { 
  Swords, 
  Target, 
  AlertTriangle, 
  MessageSquare, 
  Zap, 
  ShieldAlert, 
  UserCheck, 
  X,
  Copy,
  Check
} from 'lucide-react';
import { BattleCardItem } from '../../types';

interface BattleCardDetailProps {
  card: BattleCardItem | null;
  onClose: () => void;
}

export const BattleCardDetail: React.FC<BattleCardDetailProps> = ({ card, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  if (!card) return null;

  const handleCopyAll = () => {
    const text = `=== BATTLE CARD: ${card.solution_name} ===\n\n[Overview]\n${card.overview}\n\n[Why Customer Needs]\n${card.why_customer_needs}\n\n[Pain Points]\n${card.pain_points.join('\n')}\n\n[Talking Points]\n${card.talking_points.join('\n')}\n\n[Technical Advantages]\n${card.technical_advantages.join('\n')}\n\n[Common Objections]\n${card.common_objections.map(o => `Q: ${o.objection}\nA: ${o.answer}`).join('\n\n')}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 overflow-y-auto">
      <div className="bg-[#0c1322] border border-cyan-500/30 rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden shadow-glow-cyan animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 bg-[#111c33] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-500 via-purple-600 to-indigo-600 flex items-center justify-center text-white shadow-glow-violet">
              <Swords className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-white">{card.solution_name}</h3>
                <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-mono border border-rose-500/30">
                  PRESALES BATTLE CARD
                </span>
              </div>
              <p className="text-xs text-slate-400">{card.vendor} • <span className="text-cyan-400">{card.category}</span></p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyAll}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 hover:text-white transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Đã copy toàn bộ' : 'Copy Battle Card'}</span>
            </button>
            <button onClick={onClose} className="text-slate-400 hover:text-white p-1.5 rounded-md hover:bg-slate-800">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          {/* 1. Overview & Why customer needs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <h4 className="font-bold text-cyan-300 uppercase tracking-wider text-[11px] mb-2 flex items-center gap-1.5">
                <Target className="w-4 h-4 text-cyan-400" />
                <span>Positioning & Overview</span>
              </h4>
              <p className="leading-relaxed text-slate-200">{card.overview}</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <h4 className="font-bold text-emerald-300 uppercase tracking-wider text-[11px] mb-2 flex items-center gap-1.5">
                <Zap className="w-4 h-4 text-emerald-400" />
                <span>Why Customer Needs Immediately</span>
              </h4>
              <p className="leading-relaxed text-slate-200">{card.why_customer_needs}</p>
            </div>
          </div>

          {/* 2. Customer Pain Points vs Presales Talking Points */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-rose-500/20">
              <h4 className="font-bold text-rose-300 uppercase tracking-wider text-[11px] mb-2.5 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Customer Pain Points (Đánh trúng nỗi đau)</span>
              </h4>
              <ul className="space-y-2">
                {card.pain_points.map((p, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-rose-400 font-bold">✕</span>
                    <span className="leading-relaxed">{p}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-cyan-500/20">
              <h4 className="font-bold text-cyan-300 uppercase tracking-wider text-[11px] mb-2.5 flex items-center gap-1.5">
                <MessageSquare className="w-4 h-4 text-cyan-400" />
                <span>Presales Talking Points (Luận điểm bán hàng)</span>
              </h4>
              <ul className="space-y-2">
                {card.talking_points.map((t, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-cyan-400 font-bold">✓</span>
                    <span className="leading-relaxed text-slate-200 font-medium">{t}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* 3. Technical Advantages */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-violet-500/20">
            <h4 className="font-bold text-violet-300 uppercase tracking-wider text-[11px] mb-2.5 flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-violet-400" />
              <span>Technical Advantages over Competitors (Ưu thế kỹ thuật độc nhất)</span>
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {card.technical_advantages.map((adv, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-slate-800/80 border border-slate-700/60 leading-relaxed">
                  <span className="text-violet-400 font-bold block mb-1">#0{idx + 1} Advantage</span>
                  <span>{adv}</span>
                </div>
              ))}
            </div>
          </div>

          {/* 4. Common Objections & Objection Handling */}
          <div>
            <h4 className="font-bold text-amber-300 uppercase tracking-wider text-[11px] mb-3 flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>Common Objections & Objection Handling (Xử lý từ chối)</span>
            </h4>
            <div className="space-y-3">
              {card.common_objections.map((obj, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800">
                  <div className="flex items-start gap-2 text-rose-300 font-semibold mb-2">
                    <span className="px-1.5 py-0.5 rounded bg-rose-500/20 text-[10px] font-mono shrink-0">OBJECTION</span>
                    <span>"{obj.objection}"</span>
                  </div>
                  <div className="flex items-start gap-2 text-emerald-300 font-medium pl-2 border-l-2 border-emerald-500/40">
                    <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-[10px] font-mono shrink-0">ANSWER PRO</span>
                    <span className="leading-relaxed text-slate-200">{obj.answer}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 5. Target Buyer Personas */}
          {card.target_buyer_personas && (
            <div className="flex items-center gap-2 pt-2 text-slate-400">
              <UserCheck className="w-4 h-4 text-cyan-400" />
              <span className="font-semibold text-[11px]">Target Personas:</span>
              <div className="flex flex-wrap gap-1.5">
                {card.target_buyer_personas.map((persona, idx) => (
                  <span key={idx} className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 text-[10px] border border-slate-700">
                    {persona}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
