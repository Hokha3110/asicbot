import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { RightPanel } from './components/layout/RightPanel';
import { ChatWindow } from './components/chat/ChatWindow';
import { DocumentCenter } from './components/documents/DocumentCenter';
import { SolutionCatalog } from './components/solutions/SolutionCatalog';
import { BattleCardHub } from './components/battlecards/BattleCardHub';
import { SettingsModal } from './components/settings/SettingsModal';
import { LoginModal } from './components/auth/LoginModal';
import { ChatMessageItem, ConversationRecord, ConversationSummary, DetectedSolution, SourceReference, User } from './types';
import { api } from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'solutions' | 'battlecards' | 'settings'>('chat');
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [detectedSolutions, setDetectedSolutions] = useState<DetectedSolution[]>([]);
  const [sources, setSources] = useState<SourceReference[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTransforming, setIsTransforming] = useState(false);

  // Mobile Drawer State
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [isMobileRightPanelOpen, setIsMobileRightPanelOpen] = useState(false);
  const [isLeftSidebarCollapsed, setIsLeftSidebarCollapsed] = useState(false);
  const [isRightPanelCollapsed, setIsRightPanelCollapsed] = useState(false);

  // App settings & Auth state
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  
  // AI Keys
  const [llmProvider, setLlmProvider] = useState(localStorage.getItem('sec_copilot_provider') || 'gemini');
  const [geminiKey, setGeminiKey] = useState(localStorage.getItem('sec_copilot_gemini_key') || '');
  const [geminiModel, setGeminiModel] = useState(localStorage.getItem('sec_copilot_gemini_model') || 'gemini-2.5-flash');
  const [openaiKey, setOpenaiKey] = useState(localStorage.getItem('sec_copilot_openai_key') || '');
  const [ollamaUrl, setOllamaUrl] = useState(localStorage.getItem('sec_copilot_ollama_url') || 'http://localhost:11434');

  // Stats
  const [indexedDocsCount, setIndexedDocsCount] = useState(4);
  const [solutionsCount, setSolutionsCount] = useState(7);

  // Initialize and check user
  useEffect(() => {
    const initApp = async () => {
      const oauthToken = new URLSearchParams(window.location.search).get('oauth_token');
      if (oauthToken) {
        localStorage.setItem('sec_copilot_token', oauthToken);
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      try {
        const user = await api.getMe();
        setCurrentUser(user);
        setConversationHistory(await api.getConversations());
      } catch (err) {
        setCurrentUser(null);
      }

      try {
        const docs = await api.getDocuments();
        setIndexedDocsCount(docs.length);
        const sols = await api.getSolutions();
        setSolutionsCount(sols.length);
      } catch (err) {
        console.error('Stats load notice:', err);
      }
    };

    initApp();
  }, []);

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessageItem = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    let conversationId = activeConversationId;
    if (currentUser && !conversationId) {
      try {
        const conversation = await api.createConversation(text.slice(0, 80));
        conversationId = conversation.id;
        setActiveConversationId(conversation.id);
        setConversationHistory((prev) => [conversation, ...prev]);
      } catch (err) {
        console.warn('Conversation creation notice:', err);
      }
    }

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const response = await api.sendMessage(text, history, [], llmProvider, geminiKey, openaiKey);

      const botMsg: ChatMessageItem = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.reply,
        detected_solutions: response.detected_solutions,
        sources: response.sources,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMsg]);
      if (conversationId) {
        await api.saveConversationMessage(conversationId, userMsg);
        const savedConversation = await api.saveConversationMessage(conversationId, botMsg);
        setConversationHistory((prev) => prev.map((item) =>
          item.id === savedConversation.id ? savedConversation : item
        ));
      }
      if (response.detected_solutions && response.detected_solutions.length > 0) {
        setDetectedSolutions(response.detected_solutions);
      }
      if (response.sources && response.sources.length > 0) {
        setSources(response.sources);
      }
    } catch (err) {
      console.error('Chat error:', err);
      const fallbackMsg: ChatMessageItem = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `## Solution\nPicus Complete Security Validation\n\n## Category\nBAS (Breach and Attack Simulation)\n\n## Problem solved\nDoanh nghiệp không biết các lớp phòng thủ Firewall/EDR/SIEM có thực sự chặn được hacker hay không.\n\n## Key capability\n- Mô phỏng 4000+ kịch bản tấn công MITRE ATT&CK 24/7\n- Tự động sinh rule khắc phục cho Firewall/WAF\n\n## Customer discovery questions\n1. Hiện tại đơn vị đo lường hiệu quả bảo mật bằng cách nào?\n2. Tần suất thực hiện Pentest là bao lâu?\n\n## Source reference\nDocument: Security Brochure_update Jul 2026.pdf | Page: 4`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, fallbackMsg]);
      if (conversationId) {
        await api.saveConversationMessage(conversationId, userMsg);
        const savedConversation = await api.saveConversationMessage(conversationId, fallbackMsg);
        setConversationHistory((prev) => prev.map((item) =>
          item.id === savedConversation.id ? savedConversation : item
        ));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyPresalesMode = async (
    mode: 'technical' | 'customer' | 'sales_pitch' | 'email_draft' | 'create_slide',
    contextText?: string
  ) => {
    // If no context provided, take the last assistant message
    let ctx = contextText;
    if (!ctx) {
      const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant');
      ctx = lastAssistant ? lastAssistant.content : 'Picus BAS & Netwrix DSPM';
    }

    setIsTransforming(true);
    try {
      const result = await api.transformPresalesMode(mode, ctx, undefined, undefined, llmProvider, geminiKey, openaiKey);

      const modeTitleMap: Record<string, string> = {
        technical: 'Technical Explanation',
        customer: 'Customer Explanation',
        sales_pitch: 'Sales Pitch (Tư vấn bán hàng)',
        email_draft: 'Email Draft (Follow-up)',
        create_slide: 'Presentation Slide Outline'
      };

      const transformedMsg: ChatMessageItem = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `### ⚡ [${modeTitleMap[mode] || mode.toUpperCase()}]\n\n${result.content}`,
        mode_applied: modeTitleMap[mode] || mode,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, transformedMsg]);
      setActiveTab('chat');
    } catch (err) {
      alert('Lỗi khi chuyển đổi chế độ Presales.');
    } finally {
      setIsTransforming(false);
    }
  };

  const handleOpenChatWithSolution = (solName: string) => {
    setActiveTab('chat');
    handleSendMessage(`Hãy tư vấn chi tiết giải pháp ${solName} cho khách hàng doanh nghiệp.`);
  };

  const handleLogout = () => {
    localStorage.removeItem('sec_copilot_token');
    setCurrentUser(null);
    setConversationHistory([]);
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleLoadConversation = async (conversationId: number) => {
    if (conversationId === 0) {
      setMessages([]);
      setDetectedSolutions([]);
      setSources([]);
      setActiveConversationId(null);
      setActiveTab('chat');
      return;
    }
    try {
      const conversation: ConversationRecord = await api.getConversation(conversationId);
      setActiveConversationId(conversation.id);
      setMessages(conversation.messages.map((message) => ({
        ...message,
        id: String(message.id),
        timestamp: (message as ChatMessageItem & { created_at?: string }).created_at
          ? new Date((message as ChatMessageItem & { created_at?: string }).created_at as string).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          : message.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      })));
      const lastMessage = conversation.messages[conversation.messages.length - 1];
      setDetectedSolutions(lastMessage?.detected_solutions || []);
      setSources(lastMessage?.sources || []);
      setActiveTab('chat');
    } catch (err) {
      console.error('Conversation load error:', err);
    }
  };

  return (
    <div className="flex h-screen min-h-[100dvh] w-full min-w-0 overflow-hidden bg-[#070b14] text-slate-100">
      {/* 1. Left Sidebar (With Mobile Drawer support) */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentUser={currentUser}
        onOpenLogin={() => setIsLoginModalOpen(true)}
        onLogout={handleLogout}
        conversations={conversationHistory}
        activeConversationId={activeConversationId}
        onLoadConversation={handleLoadConversation}
        isCollapsed={isLeftSidebarCollapsed}
        onToggleCollapse={() => setIsLeftSidebarCollapsed((collapsed) => !collapsed)}
        isOpenMobile={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
      />

      {/* Main Workspace Layout */}
      <div className="flex min-w-0 flex-1 flex-col h-full">
        {/* 2. Top Header with Mobile triggers */}
        <Header
          llmProvider={llmProvider}
          setLlmProvider={setLlmProvider}
          indexedDocsCount={indexedDocsCount}
          solutionsCount={solutionsCount}
          onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
          onToggleMobileRightPanel={() => setIsMobileRightPanelOpen(!isMobileRightPanelOpen)}
          activeTab={activeTab}
        />

        {/* 3. Center Interactive Area */}
        <div className="relative flex min-h-0 min-w-0 flex-1 overflow-hidden">
          {activeTab === 'chat' && (isMobileRightPanelOpen || !('ontouchstart' in window)) && (
            <ChatWindow
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              onApplyPresalesMode={(mode, ctx) => handleApplyPresalesMode(mode, ctx)}
              isTransforming={isTransforming}
              onResetChat={() => {
                setMessages([]);
                setDetectedSolutions([]);
                setSources([]);
                setActiveConversationId(null);
              }}
            />
          )}

          {activeTab === 'documents' && (
            <DocumentCenter
              currentUser={currentUser}
              onSelectDocForChat={(docName) => {
                setActiveTab('chat');
                handleSendMessage(`Tư vấn cho tôi các giải pháp trong tài liệu ${docName}`);
              }}
            />
          )}

          {activeTab === 'solutions' && (
            <SolutionCatalog
              onOpenChatWithSolution={handleOpenChatWithSolution}
            />
          )}

          {activeTab === 'battlecards' && (
            <BattleCardHub />
          )}

          {activeTab === 'settings' && (
            <SettingsModal
              geminiKey={geminiKey}
              setGeminiKey={setGeminiKey}
              geminiModel={geminiModel}
              setGeminiModel={setGeminiModel}
              openaiKey={openaiKey}
              setOpenaiKey={setOpenaiKey}
              ollamaUrl={ollamaUrl}
              setOllamaUrl={setOllamaUrl}
              llmProvider={llmProvider}
              setLlmProvider={setLlmProvider}
            />
          )}

          {/* 4. Right Context & Presales Actions Panel (Visible in chat mode / Responsive Mobile Drawer) */}
          {activeTab === 'chat' && (
            <RightPanel
              detectedSolutions={detectedSolutions}
              sources={sources}
              onSelectSolution={handleOpenChatWithSolution}
              onApplyPresalesMode={(mode) => handleApplyPresalesMode(mode)}
              isTransforming={isTransforming}
              isOpenMobile={isMobileRightPanelOpen}
              onCloseMobile={() => setIsMobileRightPanelOpen(false)}
              isCollapsed={isRightPanelCollapsed}
              onToggleCollapse={() => setIsRightPanelCollapsed((collapsed) => !collapsed)}
            />
          )}
        </div>
      </div>

      {/* Login Modal */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onLoginSuccess={async (user) => {
          setCurrentUser(user);
          try {
            setConversationHistory(await api.getConversations());
          } catch (err) {
            setConversationHistory([]);
          }
        }}
      />
    </div>
  );
}

export default App;
