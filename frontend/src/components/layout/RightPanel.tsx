import React from 'react';
import { 
  FileText, 
  Sparkles, 
  Target, 
  X,
  Zap,
  Layers
  ,PanelRightClose
  ,Menu
} from 'lucide-react';
import { DetectedSolution, SourceReference } from '../../types';

interface RightPanelProps {
  detectedSolutions: DetectedSolution[];
  sources: SourceReference[];
  onSelectSolution: (solName: string) => void;
  onApplyPresalesMode: (mode: 'technical' | 'customer' | 'sales_pitch' | 'email_draft' | 'create_slide') => void;
  isTransforming: boolean;
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export const RightPanel: React.FC<RightPanelProps> = ({
  detectedSolutions,
  sources,
  onSelectSolution,
  onApplyPresalesMode,
  isTransforming,
  isOpenMobile = false,
  onCloseMobile
  ,isCollapsed = false
  ,onToggleCollapse
}) => {
  const modes = [
    { id: 'technical', label: 'Technical Explanation', desc: 'Kiến trúc & Tích hợp' },
    { id: 'customer', label: 'Customer Explanation', desc: 'Ngôn ngữ dễ hiểu' },
    { id: 'sales_pitch', label: 'Sales Pitch', desc: 'Nỗi đau & ROI' },
    { id: 'email_draft', label: 'Email Draft', desc: 'Thư Follow-up' },
    { id: 'create_slide', label: 'Create Slide', desc: 'Dàn ý 5-7 slide' },
  ];

  return (
    <>
      {isOpenMobile && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden animate-in fade-in duration-200"
        />
      )}

      <aside className={`
        fixed md:static inset-y-0 right-0 z-50
        ${isCollapsed ? 'w-14 overflow-hidden' : 'w-80'} bg-[#09110d] border-l border-emerald-950/80 flex flex-col h-screen md:h-full shrink-0 md:relative
        transform transition-[width,border-color,transform] duration-300 ease-in-out
        ${isOpenMobile ? 'translate-x-0 shadow-2xl' : 'translate-x-full md:translate-x-0'}
      `}>
        {isCollapsed && (
          <div className="hidden md:flex flex-col items-center gap-3 pt-3">
            <button
              onClick={onToggleCollapse}
              className="w-9 h-9 flex items-center justify-center rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-800 hover:bg-emerald-900"
              title="Mở panel phải"
            >
              <Menu className="w-5 h-5" />
            </button>
            <button
              onClick={() => onToggleCollapse?.()}
              className="w-9 h-9 flex items-center justify-center rounded-lg text-emerald-300 hover:bg-emerald-950/60"
              title="Presales modes"
            >
              <Sparkles className="w-4 h-4" />
            </button>
            <button
              onClick={() => onToggleCollapse?.()}
              className="w-9 h-9 flex items-center justify-center rounded-lg text-slate-400 hover:bg-emerald-950/60 hover:text-emerald-300"
              title="Solutions detected"
            >
              <Target className="w-4 h-4" />
            </button>
            <button
              onClick={() => onToggleCollapse?.()}
              className="w-9 h-9 flex items-center justify-center rounded-lg text-slate-400 hover:bg-emerald-950/60 hover:text-emerald-300"
              title="Source references"
            >
              <FileText className="w-4 h-4" />
            </button>
          </div>
        )}
        {!isCollapsed && onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            className="hidden md:flex absolute right-2 top-3 z-10 w-8 h-8 items-center justify-center rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-800 hover:bg-emerald-900"
            title="Thu panel phải"
          >
            <PanelRightClose className="w-4 h-4" />
          </button>
        )}

        {!isCollapsed && <div className="h-full min-w-0 overflow-y-auto p-4 space-y-5">
        {/* Mobile Header */}
        <div className="flex items-center justify-between md:hidden pb-3 border-b border-emerald-950">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-bold text-white uppercase">Presales Modes & Solutions</span>
          </div>
          <button
            onClick={onCloseMobile}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-emerald-950"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 1. Quick Presales Modes */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Presales Fast Modes
            </h3>
          </div>
          <p className="text-[11px] text-slate-400 mb-3">
            Chuyển đổi nội dung theo đối tượng tư vấn:
          </p>
          <div className="grid grid-cols-1 gap-1.5">
            {modes.map((m) => (
              <button
                key={m.id}
                onClick={() => {
                  onApplyPresalesMode(m.id as any);
                  if (onCloseMobile) onCloseMobile();
                }}
                disabled={isTransforming}
                className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-surface-900 hover:bg-emerald-950/70 border border-emerald-950 hover:border-emerald-800 text-xs font-medium text-slate-300 hover:text-emerald-300 transition-all text-left"
              >
                <div>
                  <span className="block font-semibold">[{m.label}]</span>
                  <span className="text-[10px] text-slate-400">{m.desc}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 2. Detected Solutions in Context */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Solutions Detected
              </h3>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 font-mono font-bold border border-emerald-800/60">
              {detectedSolutions.length}
            </span>
          </div>

          {detectedSolutions.length === 0 ? (
            <div className="p-4 rounded-xl bg-surface-900 border border-emerald-950 text-center">
              <p className="text-xs text-slate-400">Chưa có giải pháp cụ thể.</p>
              <p className="text-[11px] text-slate-400 mt-1">VD: Hỏi về "Picus", "bảo vệ dữ liệu DSPM", "Graylog"...</p>
            </div>
          ) : (
            <div className="space-y-2">
              {detectedSolutions.map((sol, index) => (
                <div
                  key={index}
                  onClick={() => {
                    onSelectSolution(sol.name);
                    if (onCloseMobile) onCloseMobile();
                  }}
                  className="p-3 rounded-xl glass-card cursor-pointer group"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-emerald-300 group-hover:text-emerald-200 transition-colors">
                        {sol.name}
                      </h4>
                      <p className="text-[11px] text-slate-400">{sol.vendor}</p>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono border border-emerald-900">
                      {sol.category}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-300 mt-2 line-clamp-2 leading-relaxed">
                    {sol.summary}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 3. Document Source References */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Source Reference
              </h3>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 font-mono font-bold border border-emerald-800/60">
              {sources.length}
            </span>
          </div>

          {sources.length === 0 ? (
            <div className="p-3 rounded-xl bg-surface-900 border border-emerald-950 text-center">
              <p className="text-xs text-slate-400">Nguồn trích dẫn sẽ hiển thị khi RAG tìm thấy tài liệu liên quan.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sources.map((src, index) => (
                <div key={index} className="p-2.5 rounded-xl bg-surface-900 border border-emerald-950 text-xs">
                  <div className="flex items-center justify-between text-slate-300 font-semibold mb-1">
                    <span className="truncate max-w-[170px] text-slate-200">{src.document_name}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                      p.{src.page_number}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2 italic">
                    "{src.snippet}"
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
        </div>}
      </aside>
    </>
  );
};
