import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowUpRight, HelpCircle, Tag, ExternalLink } from 'lucide-react';
import { SolutionItem } from '../../types';
import { api } from '../../services/api';
import { SmartSearch } from './SmartSearch';
import { SolutionDetailModal } from './SolutionDetailModal';

interface SolutionCatalogProps {
  onOpenChatWithSolution: (solName: string) => void;
}

export const SolutionCatalog: React.FC<SolutionCatalogProps> = ({ onOpenChatWithSolution }) => {
  const [solutions, setSolutions] = useState<SolutionItem[]>([]);
  const [displayedSolutions, setDisplayedSolutions] = useState<SolutionItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSolution, setSelectedSolution] = useState<SolutionItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchSolutions = async () => {
    setIsLoading(true);
    try {
      const data = await api.getSolutions();
      setSolutions(data);
      setDisplayedSolutions(data);
    } catch (err) {
      console.error('Failed to fetch solutions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSolutions();
  }, []);

  const handleCategoryFilter = (cat: string) => {
    setSelectedCategory(cat);
    if (cat === 'all') {
      setDisplayedSolutions(solutions);
    } else {
      setDisplayedSolutions(solutions.filter((s) => s.category.toLowerCase().includes(cat.toLowerCase())));
    }
  };

  const handleSmartSearchResults = (results: SolutionItem[]) => {
    setDisplayedSolutions(results);
    setSelectedCategory('all');
  };

  const categories = ['all', 'BAS', 'DSPM', 'Identity', 'SOC', 'DevSecOps'];

  return (
    <div className="min-w-0 flex-1 flex flex-col h-full bg-[#070b09] overflow-y-auto overflow-x-hidden p-4 sm:p-6 md:p-8">
      {/* Page Title */}
      <div className="mb-6">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-glow-jade">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-white tracking-wide">
              Solution Database & Presales Catalog
            </h2>
            <p className="text-xs text-slate-400">
              Tra cứu giải pháp an toàn thông tin, năng lực kỹ thuật và đối thủ cạnh tranh
            </p>
          </div>
        </div>
      </div>

      {/* Smart Search Banner */}
      <SmartSearch
        onResults={handleSmartSearchResults}
        onClear={() => setDisplayedSolutions(solutions)}
      />

      {/* Category Pills */}
      <div className="flex min-h-9 items-center gap-1.5 overflow-x-auto pb-1 mb-3">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => handleCategoryFilter(cat)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition-all shrink-0 ${
              selectedCategory === cat
                ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40 shadow-glow-jade'
                : 'bg-surface-900 text-slate-400 hover:text-slate-200 border border-emerald-950'
            }`}
          >
            {cat === 'all' ? 'Tất cả' : cat}
          </button>
        ))}
      </div>

      {/* Solution Grid Cards */}
      <div className="min-w-0 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayedSolutions.map((sol) => (
          <div
            key={sol.id}
            onClick={() => setSelectedSolution(sol)}
            className="min-w-0 glass-card rounded-2xl p-5 flex flex-col justify-between cursor-pointer group"
          >
            <div>
              {/* Header info */}
              <div className="flex items-start justify-between mb-2.5">
                <div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-900 uppercase">
                    {sol.category}
                  </span>
                  <h3 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors mt-2">
                    {sol.name}
                  </h3>
                  <p className="text-xs text-slate-400">{sol.vendor}</p>
                </div>
                <div className="p-1 rounded-lg bg-surface-900 text-slate-400 group-hover:text-emerald-300 group-hover:bg-emerald-950 transition-all shrink-0">
                  <ArrowUpRight className="w-4 h-4" />
                </div>
              </div>

              {/* Problem Solved */}
              <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed mb-3">
                {sol.problem}
              </p>

              {/* Key Features Preview */}
              <div className="space-y-1 mb-3">
                {(sol.features || []).slice(0, 2).map((feat, idx) => (
                  <div key={idx} className="flex items-center gap-1.5 text-[11px] text-slate-300 truncate">
                    <span className="text-emerald-400 font-bold">▹</span>
                    <span className="truncate">{feat}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom tags & Actions */}
            <div className="pt-3 border-t border-emerald-950 flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1 text-slate-400">
                <HelpCircle className="w-3.5 h-3.5 text-emerald-400" />
                <span>{sol.discovery_questions?.length || 0} Discovery Qs</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onOpenChatWithSolution(sol.name);
                }}
                className="px-2.5 py-1 rounded-lg bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 text-[10px] font-bold transition-all"
              >
                Chat Tư Vấn
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Detail Modal */}
      <SolutionDetailModal
        solution={selectedSolution}
        onClose={() => setSelectedSolution(null)}
        onOpenChatWithSolution={onOpenChatWithSolution}
      />
    </div>
  );
};
