import React from 'react';
import { FileText, Bookmark } from 'lucide-react';
import { SourceReference } from '../../types';

interface SourceBadgeProps {
  sources: SourceReference[];
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-2.5 border-t border-emerald-950/80 flex flex-wrap items-center gap-1.5 text-xs">
      <div className="flex items-center gap-1 text-slate-400 font-semibold text-[10px] uppercase tracking-wider">
        <Bookmark className="w-3 h-3 text-emerald-400" />
        <span>Sources:</span>
      </div>
      {sources.map((src, idx) => (
        <span
          key={idx}
          className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-emerald-950/70 border border-emerald-800/50 text-emerald-300 text-[11px] font-mono"
        >
          <FileText className="w-3 h-3 text-emerald-400" />
          <span className="max-w-[180px] truncate">{src.document_name}</span>
          <span className="bg-emerald-500/20 px-1 py-0.2 rounded text-[10px] text-emerald-200">
            p.{src.page_number}
          </span>
        </span>
      ))}
    </div>
  );
};
