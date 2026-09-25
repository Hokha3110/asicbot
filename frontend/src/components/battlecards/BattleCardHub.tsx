import React, { useState, useEffect } from 'react';
import { Swords, Plus, Sparkles, Loader2, ArrowRight } from 'lucide-react';
import { BattleCardItem } from '../../types';
import { api } from '../../services/api';
import { BattleCardDetail } from './BattleCardDetail';

export const BattleCardHub: React.FC = () => {
  const [battlecards, setBattlecards] = useState<BattleCardItem[]>([]);
  const [selectedCard, setSelectedCard] = useState<BattleCardItem | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [genSolutionName, setGenSolutionName] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchBattleCards = async () => {
    setIsLoading(true);
    try {
      const data = await api.getBattleCards();
      setBattlecards(data);
    } catch (err) {
      console.error('Failed to load battlecards:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBattleCards();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!genSolutionName.trim() || isGenerating) return;

    setIsGenerating(true);
    try {
      const newCard = await api.generateBattleCard(genSolutionName.trim());
      setGenSolutionName('');
      fetchBattleCards();
      setSelectedCard(newCard);
    } catch (err) {
      alert('Lỗi khi sinh Battle Card.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#070b09] overflow-y-auto p-4 sm:p-6 md:p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-glow-jade">
            <Swords className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-white tracking-wide">
              Solution Battle Cards
            </h2>
            <p className="text-xs text-slate-400">
              Vũ khí cạnh tranh: Luận điểm bán hàng, xử lý từ chối (Objection Handling) & ưu thế kỹ thuật
            </p>
          </div>
        </div>
      </div>

      {/* AI BattleCard Generator Box */}
      <div className="glass-panel-glow rounded-2xl p-4 sm:p-5 mb-6 border-emerald-950">
        <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="flex items-center gap-1.5 text-slate-200 text-xs font-bold uppercase tracking-wider shrink-0">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>AI BattleCard Generator:</span>
          </div>
          <input
            type="text"
            value={genSolutionName}
            onChange={(e) => setGenSolutionName(e.target.value)}
            placeholder="Nhập tên giải pháp cần sinh Battle Card (VD: CrowdStrike, Snyk, CyberArk...)"
            className="flex-1 bg-[#0b1612] border border-emerald-950 rounded-xl px-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
          <button
            type="submit"
            disabled={!genSolutionName.trim() || isGenerating}
            className="w-full sm:w-auto px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-xs font-bold text-white shadow-glow-jade hover:from-emerald-500 hover:to-teal-500 flex items-center justify-center gap-2 shrink-0 disabled:opacity-50"
          >
            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            <span>Tạo mới</span>
          </button>
        </form>
      </div>

      {/* Battle Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {battlecards.map((card) => (
          <div
            key={card.id}
            onClick={() => setSelectedCard(card)}
            className="glass-card rounded-2xl p-5 flex flex-col justify-between cursor-pointer border border-emerald-950/80 hover:border-emerald-700/60 group"
          >
            <div>
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-900 uppercase">
                  {card.category}
                </span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {card.common_objections?.length || 0} Objections Handled
                </span>
              </div>

              <h3 className="text-sm sm:text-base font-bold text-white group-hover:text-emerald-300 transition-colors mb-0.5">
                {card.solution_name}
              </h3>
              <p className="text-xs text-slate-400 mb-3">{card.vendor}</p>

              <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed mb-3">
                {card.overview}
              </p>

              {/* Pain Point Highlight */}
              <div className="p-2.5 rounded-xl bg-surface-900 border border-emerald-950 text-xs text-slate-300 mb-3">
                <span className="font-bold block text-[10px] uppercase tracking-wider text-emerald-400 mb-0.5">Customer Pain Point:</span>
                <p className="line-clamp-2">{card.pain_points?.[0] || 'Chưa cập nhật'}</p>
              </div>
            </div>

            {/* View Full Battle Card Button */}
            <div className="pt-2.5 border-t border-emerald-950 flex items-center justify-between text-xs text-emerald-400 font-semibold group-hover:text-emerald-300">
              <span>Chi tiết Battle Card</span>
              <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        ))}
      </div>

      {/* Detail Modal */}
      <BattleCardDetail
        card={selectedCard}
        onClose={() => setSelectedCard(null)}
      />
    </div>
  );
};
