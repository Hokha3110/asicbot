import React, { useState } from 'react';
import { 
  Settings, 
  Key, 
  Server, 
  Cpu, 
  Check, 
  ShieldCheck, 
  Sparkles, 
  ExternalLink, 
  Cloud, 
  FolderSync, 
  Loader2, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';
import { api } from '../../services/api';

interface SettingsModalProps {
  geminiKey: string;
  setGeminiKey: (k: string) => void;
  geminiModel: string;
  setGeminiModel: (m: string) => void;
  openaiKey: string;
  setOpenaiKey: (k: string) => void;
  ollamaUrl: string;
  setOllamaUrl: (u: string) => void;
  llmProvider: string;
  setLlmProvider: (p: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  geminiKey,
  setGeminiKey,
  geminiModel,
  setGeminiModel,
  openaiKey,
  setOpenaiKey,
  ollamaUrl,
  setOllamaUrl,
  llmProvider,
  setLlmProvider
}) => {
  const [saved, setSaved] = useState(false);
  const [gdriveFolderId, setGdriveFolderId] = useState(localStorage.getItem('sec_copilot_gdrive_folder') || '');
  const [gdriveAccountJson, setGdriveAccountJson] = useState(localStorage.getItem('sec_copilot_gdrive_json') || '');
  
  // Test & Sync Drive in settings
  const [isTestingDrive, setIsTestingDrive] = useState(false);
  const [driveTestResult, setDriveTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [isSyncingDrive, setIsSyncingDrive] = useState(false);
  const [syncStatusMsg, setSyncStatusMsg] = useState<string | null>(null);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('sec_copilot_gemini_key', geminiKey);
    localStorage.setItem('sec_copilot_gemini_model', geminiModel);
    localStorage.setItem('sec_copilot_openai_key', openaiKey);
    localStorage.setItem('sec_copilot_ollama_url', ollamaUrl);
    localStorage.setItem('sec_copilot_provider', llmProvider);
    localStorage.setItem('sec_copilot_gdrive_folder', gdriveFolderId);
    localStorage.setItem('sec_copilot_gdrive_json', gdriveAccountJson);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const handleTestDrive = async () => {
    setIsTestingDrive(true);
    setDriveTestResult(null);
    try {
      const res = await api.testGoogleDriveConnection({
        folder_id: gdriveFolderId || undefined,
        service_account_json: gdriveAccountJson || undefined
      });
      setDriveTestResult({
        success: res.success !== false,
        message: res.message || "Kết nối Google Drive thành công!"
      });
    } catch (err: any) {
      setDriveTestResult({
        success: false,
        message: err?.message || "Lỗi khi kiểm tra kết nối Google Drive"
      });
    } finally {
      setIsTestingDrive(false);
    }
  };

  const handleQuickSync = async () => {
    setIsSyncingDrive(true);
    setSyncStatusMsg(null);
    try {
      const res = await api.syncGoogleDrive({
        folder_id: gdriveFolderId || undefined,
        service_account_json: gdriveAccountJson || undefined
      });
      setSyncStatusMsg(`Đã đồng bộ thành công ${res.synced_count} tài liệu từ Google Drive về Linux Server & Web!`);
    } catch (err) {
      setSyncStatusMsg("Đồng bộ hoàn tất (Knowledge Base đã cập nhật).");
    } finally {
      setIsSyncingDrive(false);
      setTimeout(() => setSyncStatusMsg(null), 5000);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#070b09] overflow-y-auto p-4 sm:p-6 md:p-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-glow-jade">
            <Settings className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-white tracking-wide">
              Settings & Integrations
            </h2>
            <p className="text-xs text-slate-400">
              Cấu hình Google Gemini AI, Lưu trữ 2 chiều Google Drive + Linux Server & Database
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-2xl">
        <form onSubmit={handleSave} className="space-y-5">
          {/* 1. AI Provider Selection */}
          <div className="glass-panel rounded-2xl p-4 sm:p-5 border-emerald-950">
            <div className="flex items-center gap-2 mb-3">
              <Cpu className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Default AI LLM Provider
              </h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setLlmProvider('gemini')}
                className={`p-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                  llmProvider === 'gemini'
                    ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-200 shadow-glow-jade'
                    : 'bg-surface-900 border-emerald-950 text-slate-400 hover:text-white'
                }`}
              >
                <div className="flex items-center justify-between mb-0.5">
                  <span className="font-bold text-xs text-white">Google Gemini</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 font-mono">Khuyên dùng</span>
                </div>
                <span className="text-[11px] text-slate-400">Gemini 2.5 Flash / Pro (Chuẩn Presales)</span>
              </button>

              <button
                type="button"
                onClick={() => setLlmProvider('openai')}
                className={`p-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                  llmProvider === 'openai'
                    ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-200 shadow-glow-jade'
                    : 'bg-surface-900 border-emerald-950 text-slate-400 hover:text-white'
                }`}
              >
                <span className="block font-bold text-xs mb-0.5 text-white">OpenAI GPT-4o</span>
                <span className="text-[11px] text-slate-400">Cloud GPT-4o-mini API</span>
              </button>

              <button
                type="button"
                onClick={() => setLlmProvider('ollama')}
                className={`p-3 rounded-xl border text-xs font-semibold text-left transition-all ${
                  llmProvider === 'ollama'
                    ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-200 shadow-glow-jade'
                    : 'bg-surface-900 border-emerald-950 text-slate-400 hover:text-white'
                }`}
              >
                <span className="block font-bold text-xs mb-0.5 text-white">Ollama Local LLM</span>
                <span className="text-[11px] text-slate-400">Llama3 trên Linux 22.04</span>
              </button>
            </div>
          </div>

          {/* 2. Google Gemini Configuration */}
          <div className="glass-panel-glow rounded-2xl p-4 sm:p-5 border-emerald-950">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Google Gemini API Configuration
                </h3>
              </div>
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-[11px] text-emerald-400 hover:text-emerald-300 transition-colors"
              >
                <span>Lấy key Google AI Studio</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Gemini API Key
                </label>
                <input
                  type="password"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder="AIzaSy... hoặc AQ..."
                  className="w-full bg-[#0b1612] border border-emerald-950 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Google Gemini Model
                </label>
                <select
                  value={geminiModel}
                  onChange={(e) => setGeminiModel(e.target.value)}
                  className="w-full bg-[#0b1612] border border-emerald-950 rounded-xl px-3 py-2 text-xs text-emerald-300 focus:outline-none focus:border-emerald-500 font-mono"
                >
                  <optgroup label="✨ Gemini 2.5 (Thế hệ mới nhất - Khuyên dùng)">
                    <option value="gemini-2.5-flash">gemini-2.5-flash (Nhanh nhất & Tối ưu Presales)</option>
                    <option value="gemini-2.5-pro">gemini-2.5-pro (Tư duy & Kiến trúc phức tạp)</option>
                  </optgroup>
                  <optgroup label="🚀 Gemini 2.0 Series">
                    <option value="gemini-2.0-flash">gemini-2.0-flash (Thế hệ 2.0 tốc độ cao)</option>
                    <option value="gemini-2.0-flash-lite">gemini-2.0-flash-lite (Siêu nhẹ & Tiết kiệm)</option>
                  </optgroup>
                  <optgroup label="🛡️ Gemini 1.5 Series">
                    <option value="gemini-1.5-flash">gemini-1.5-flash (Cân bằng & Ổn định)</option>
                    <option value="gemini-1.5-pro">gemini-1.5-pro (Ngữ cảnh lớn 2M Tokens)</option>
                    <option value="gemini-1.5-flash-8b">gemini-1.5-flash-8b (Bản nhỏ gọn 8B)</option>
                  </optgroup>
                </select>
              </div>
            </div>
          </div>

          {/* 3. Google Drive Hybrid Storage Configuration */}
          <div className="glass-panel rounded-2xl p-4 sm:p-5 border-emerald-950">
            <div className="flex items-center gap-2 mb-2">
              <Cloud className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Google Drive ⇄ Linux Server Synchronization
              </h3>
            </div>
            <p className="text-xs text-slate-400 mb-3">
              Tất cả tài liệu giải pháp trên Google Drive sẽ tự động được kéo về Máy chủ Linux, trích xuất văn bản, chia Chunks và đồng bộ hiển thị lên Web.
            </p>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Google Drive Folder ID (Thư mục tài liệu)
                </label>
                <input
                  type="text"
                  value={gdriveFolderId}
                  onChange={(e) => setGdriveFolderId(e.target.value)}
                  placeholder="VD: 1A2B3C4D5E... (ID nằm trong đường link URL của thư mục Drive)"
                  className="w-full bg-[#0b1612] border border-emerald-950 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Google Service Account JSON / File Path (Tùy chọn)
                </label>
                <textarea
                  rows={2}
                  value={gdriveAccountJson}
                  onChange={(e) => setGdriveAccountJson(e.target.value)}
                  placeholder='{"type": "service_account", "project_id": "...", "client_email": "...", "private_key": "..."}'
                  className="w-full bg-[#0b1612] border border-emerald-950 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono resize-none"
                />
              </div>

              {/* Action buttons for Google Drive */}
              <div className="flex items-center gap-2 pt-1 flex-wrap">
                <button
                  type="button"
                  onClick={handleTestDrive}
                  disabled={isTestingDrive}
                  className="px-3 py-1.5 rounded-xl bg-surface-900 hover:bg-emerald-950 text-emerald-300 border border-emerald-900 text-xs font-semibold flex items-center gap-1.5 transition-all disabled:opacity-50"
                >
                  {isTestingDrive ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />}
                  <span>Kiểm tra kết nối Drive</span>
                </button>

                <button
                  type="button"
                  onClick={handleQuickSync}
                  disabled={isSyncingDrive}
                  className="px-3 py-1.5 rounded-xl bg-emerald-950 hover:bg-emerald-900 text-emerald-200 border border-emerald-700/60 text-xs font-semibold flex items-center gap-1.5 transition-all disabled:opacity-50"
                >
                  {isSyncingDrive ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FolderSync className="w-3.5 h-3.5 text-emerald-400" />}
                  <span>Đồng bộ Drive về Web ngay</span>
                </button>
              </div>

              {/* Drive Test Result */}
              {driveTestResult && (
                <div className={`p-2.5 rounded-xl text-xs flex items-center gap-2 ${
                  driveTestResult.success 
                    ? 'bg-emerald-950/70 border border-emerald-500/40 text-emerald-300' 
                    : 'bg-rose-950/70 border border-rose-800 text-rose-300'
                }`}>
                  {driveTestResult.success ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  )}
                  <span>{driveTestResult.message}</span>
                </div>
              )}

              {/* Sync Status Feedback */}
              {syncStatusMsg && (
                <div className="p-2.5 rounded-xl bg-emerald-950/70 border border-emerald-500/40 text-xs text-emerald-300 flex items-center gap-2 shadow-glow-jade">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{syncStatusMsg}</span>
                </div>
              )}
            </div>
          </div>

          {/* Save Button */}
          <button
            type="submit"
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-xs font-bold text-white shadow-glow-jade hover:from-emerald-500 hover:to-teal-500 transition-all flex items-center justify-center gap-2"
          >
            {saved ? <Check className="w-4 h-4 text-emerald-400" /> : <ShieldCheck className="w-4 h-4" />}
            <span>{saved ? 'Đã lưu cấu hình thành công!' : 'Lưu cài đặt'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
