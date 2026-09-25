import React from 'react';
import { 
  Bot, 
  Files, 
  ShieldCheck, 
  Swords, 
  GraduationCap, 
  Settings, 
  LogOut, 
  UserCheck, 
  X,
  MessageSquareText,
  Plus
} from 'lucide-react';
import { ConversationSummary, User } from '../../types';

interface SidebarProps {
  activeTab: 'chat' | 'documents' | 'solutions' | 'battlecards' | 'settings';
  setActiveTab: (tab: 'chat' | 'documents' | 'solutions' | 'battlecards' | 'settings') => void;
  currentUser: User | null;
  onOpenLogin: () => void;
  onLogout: () => void;
  conversations: ConversationSummary[];
  activeConversationId: number | null;
  onLoadConversation: (conversationId: number) => void;
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  currentUser,
  onOpenLogin,
  onLogout,
  conversations,
  activeConversationId,
  onLoadConversation,
  isOpenMobile = false,
  onCloseMobile
}) => {
  const navItems = [
    { id: 'chat', label: 'Kali0t Presales Chat', icon: Bot, badge: 'Kali0t' },
    { id: 'solutions', label: 'Solution Catalog', icon: ShieldCheck, badge: 'NLP' },
    { id: 'battlecards', label: 'Battle Cards', icon: Swords, badge: 'AI' },
    { id: 'documents', label: 'Document Center', icon: Files, badge: null },
    { id: 'settings', label: 'Settings & Gemini', icon: Settings, badge: null },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div 
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden animate-in fade-in duration-200"
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-64 bg-[#09110d] border-r border-emerald-950/70 flex flex-col justify-between h-screen shrink-0 select-none
        transform transition-transform duration-300 ease-in-out
        ${isOpenMobile ? 'translate-x-0 shadow-2xl' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Brand Header */}
        <div>
          <div className="p-4 border-b border-emerald-950/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-glow-jade">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h1 className="font-bold text-sm tracking-wide text-white">
                  KALI0T
                </h1>
                <p className="text-[10px] text-emerald-400 font-mono tracking-wider">AI PRESALES ARCHITECT</p>
              </div>
            </div>

            <button
              onClick={onCloseMobile}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-emerald-950 md:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Menu */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => {
                setActiveTab('chat');
                onLoadConversation(0);
                onCloseMobile?.();
              }}
              className="w-full flex items-center justify-center gap-2 px-3 py-2.5 mb-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors shadow-glow-jade"
            >
              <Plus className="w-4 h-4" />
              <span>New chat</span>
            </button>
            <div className="text-[10px] font-semibold text-emerald-600 px-3 py-1.5 uppercase tracking-wider">
              Workspace
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id as any);
                    if (onCloseMobile) onCloseMobile();
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-emerald-950/70 text-emerald-300 border border-emerald-500/30 shadow-glow-jade'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-emerald-950/30 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-500'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                      isActive 
                        ? 'bg-emerald-500/20 text-emerald-200 border border-emerald-500/30' 
                        : 'bg-surface-800 text-slate-500'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {currentUser && (
            <div className="px-3 pt-2">
              <div className="flex items-center gap-2 px-3 py-1.5 text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">
                <MessageSquareText className="w-3.5 h-3.5" />
                <span>Cuộc trò chuyện cũ</span>
              </div>
              <div className="max-h-44 overflow-y-auto space-y-1">
                {conversations.length === 0 ? (
                  <p className="px-3 py-2 text-[11px] text-slate-500">Chưa có lịch sử.</p>
                ) : conversations.map((conversation) => (
                  <button
                    key={conversation.id}
                    onClick={() => {
                      onLoadConversation(conversation.id);
                      onCloseMobile?.();
                    }}
                    className={`w-full text-left px-3 py-2 rounded-lg text-[11px] truncate transition-colors ${
                      activeConversationId === conversation.id
                        ? 'bg-emerald-950/70 text-emerald-300'
                        : 'text-slate-400 hover:bg-emerald-950/40 hover:text-slate-200'
                    }`}
                    title={conversation.title}
                  >
                    {conversation.title}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Footer */}
        <div className="p-3 border-t border-emerald-950/80 bg-[#070c09]">
          {currentUser ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-7 h-7 rounded-lg bg-emerald-900/60 border border-emerald-700/40 flex items-center justify-center text-[11px] font-bold text-emerald-300 uppercase shrink-0">
                  {currentUser.username.substring(0, 2)}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-slate-200 truncate">{currentUser.full_name || currentUser.username}</p>
                  <span className="text-[10px] text-emerald-400/80 font-mono capitalize">
                    {currentUser.role}
                  </span>
                </div>
              </div>
              <button
                onClick={onLogout}
                title="Đăng xuất"
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 rounded-lg transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => {
                onOpenLogin();
                if (onCloseMobile) onCloseMobile();
              }}
              className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-emerald-950/80 hover:bg-emerald-900/80 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition-all"
            >
              <UserCheck className="w-3.5 h-3.5" />
              <span>Đăng nhập</span>
            </button>
          )}
        </div>
      </aside>
    </>
  );
};
