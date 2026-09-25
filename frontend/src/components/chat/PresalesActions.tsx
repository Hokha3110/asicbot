import React from 'react';
import { Sparkles, Terminal, Users, TrendingUp, Mail, Presentation } from 'lucide-react';

interface PresalesActionsProps {
  onSelectMode: (mode: 'technical' | 'customer' | 'sales_pitch' | 'email_draft' | 'create_slide') => void;
  disabled?: boolean;
}

export const PresalesActions: React.FC<PresalesActionsProps> = ({ onSelectMode, disabled }) => {
  return (
    <div className="flex flex-wrap items-center gap-1.5 mt-3 pt-2.5 border-t border-emerald-950/80">
      <span className="text-[10px] font-semibold text-emerald-500/80 mr-1 flex items-center gap-1">
        <Sparkles className="w-3 h-3 text-emerald-400" />
        <span>Convert to:</span>
      </span>

      <button
        onClick={() => onSelectMode('technical')}
        disabled={disabled}
        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-surface-900 hover:bg-emerald-950 border border-emerald-950 text-[11px] font-medium text-slate-300 hover:text-emerald-300 transition-all"
      >
        <Terminal className="w-3 h-3 text-emerald-400" />
        <span>Technical</span>
      </button>

      <button
        onClick={() => onSelectMode('customer')}
        disabled={disabled}
        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-surface-900 hover:bg-emerald-950 border border-emerald-950 text-[11px] font-medium text-slate-300 hover:text-emerald-300 transition-all"
      >
        <Users className="w-3 h-3 text-emerald-400" />
        <span>Customer</span>
      </button>

      <button
        onClick={() => onSelectMode('sales_pitch')}
        disabled={disabled}
        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-surface-900 hover:bg-emerald-950 border border-emerald-950 text-[11px] font-medium text-slate-300 hover:text-emerald-300 transition-all"
      >
        <TrendingUp className="w-3 h-3 text-emerald-400" />
        <span>Sales Pitch</span>
      </button>

      <button
        onClick={() => onSelectMode('email_draft')}
        disabled={disabled}
        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-surface-900 hover:bg-emerald-950 border border-emerald-950 text-[11px] font-medium text-slate-300 hover:text-emerald-300 transition-all"
      >
        <Mail className="w-3 h-3 text-emerald-400" />
        <span>Email Draft</span>
      </button>

      <button
        onClick={() => onSelectMode('create_slide')}
        disabled={disabled}
        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-surface-900 hover:bg-emerald-950 border border-emerald-950 text-[11px] font-medium text-slate-300 hover:text-emerald-300 transition-all"
      >
        <Presentation className="w-3 h-3 text-emerald-400" />
        <span>Slide Outline</span>
      </button>
    </div>
  );
};
