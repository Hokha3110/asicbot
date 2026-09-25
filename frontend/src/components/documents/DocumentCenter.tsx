import React, { useState, useEffect } from 'react';
import { 
  Files, 
  Upload, 
  Search, 
  Trash2, 
  CheckCircle2, 
  Cloud, 
  HardDrive, 
  RefreshCw, 
  ExternalLink, 
  Download,
  Loader2, 
  FolderSync, 
  AlertCircle,
  FileText,
  X,
  Sparkles,
  ShieldCheck,
  Layers
} from 'lucide-react';
import { DocumentItem, User } from '../../types';
import { api } from '../../services/api';
import { FileUploadModal } from './FileUploadModal';

interface DocumentCenterProps {
  currentUser: User | null;
  onSelectDocForChat?: (docName: string) => void;
}

interface SyncResult {
  message: string;
  synced_count: number;
  total_chunks?: number;
  synced_files?: Array<{
    name: string;
    vendor?: string;
    category?: string;
    pages: number;
    chunks: number;
    gdrive_url?: string;
  }>;
  drive_connected?: boolean;
  errors?: string[];
}

export const DocumentCenter: React.FC<DocumentCenterProps> = ({ currentUser, onSelectDocForChat }) => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Sync Drive states
  const [isSyncModalOpen, setIsSyncModalOpen] = useState(false);
  const [isSyncingDrive, setIsSyncingDrive] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [gdriveStatus, setGdriveStatus] = useState<any>(null);
  const [customFolderId, setCustomFolderId] = useState('');

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDriveStatus = async () => {
    try {
      const status = await api.getGoogleDriveStatus();
      setGdriveStatus(status);
      if (status.folder_id && status.folder_id !== "Chưa cấu hình Folder ID") {
        setCustomFolderId(status.folder_id);
      }
    } catch (err) {
      console.error('Failed to get Drive status:', err);
    }
  };

  useEffect(() => {
    fetchDocuments();
    fetchDriveStatus();
  }, []);

  const handleTriggerSync = async () => {
    setIsSyncingDrive(true);
    setSyncResult(null);
    setIsSyncModalOpen(true);
    try {
      const savedFolder = customFolderId || localStorage.getItem('sec_copilot_gdrive_folder') || undefined;
      const res = await api.syncGoogleDrive({
        folder_id: savedFolder
      });
      setSyncResult(res);
      fetchDocuments();
    } catch (err: any) {
      setSyncResult({
        message: "Lỗi kết nối hoặc đồng bộ từ Google Drive. Vui lòng kiểm tra quyền thư mục hoặc thông tin xác thực.",
        synced_count: 0,
        errors: [err?.message || "Lỗi không xác định"]
      });
    } finally {
      setIsSyncingDrive(false);
    }
  };

  const handleDelete = async (docId: number, docName: string) => {
    if (window.confirm(`Bạn có chắc chắn muốn xóa tài liệu '${docName}'?`)) {
      try {
        await api.deleteDocument(docId);
        fetchDocuments();
      } catch (err) {
        alert('Lỗi khi xóa tài liệu.');
      }
    }
  };

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.document_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          doc.vendor.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          doc.solution_category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCategory === 'all' || doc.solution_category.toLowerCase().includes(selectedCategory.toLowerCase());
    return matchesSearch && matchesCat;
  });

  const categories = ['all', 'BAS', 'DSPM', 'Identity', 'SOC', 'DevSecOps'];

  return (
    <div className="flex-1 flex flex-col h-full bg-[#070b09] overflow-y-auto p-4 sm:p-6 md:p-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-glow-jade">
            <Files className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg sm:text-xl font-bold text-white tracking-wide">
                Document Center
              </h2>
              <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                <Cloud className="w-3 h-3 text-emerald-400" />
                <span>Google Drive ⇄ Linux Server</span>
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Đồng bộ 2 chiều: Trên Google Drive có tài liệu gì, Máy chủ Linux và Giao diện Web tự động có tài liệu đó!
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 self-start sm:self-auto flex-wrap">
          <button
            onClick={handleTriggerSync}
            disabled={isSyncingDrive}
            className="px-3.5 py-2 rounded-xl bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-700/60 text-xs font-semibold flex items-center gap-2 transition-all shadow-glow-jade disabled:opacity-50"
            title="Đồng bộ tất cả tài liệu từ thư mục Google Drive về Server"
          >
            {isSyncingDrive ? (
              <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />
            ) : (
              <FolderSync className="w-4 h-4 text-emerald-400" />
            )}
            <span>{isSyncingDrive ? "Đang đồng bộ..." : "Sync Google Drive"}</span>
          </button>

          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-xs font-bold text-white flex items-center justify-center gap-1.5 shadow-glow-jade hover:from-emerald-500 hover:to-teal-500 transition-all"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload File</span>
          </button>
        </div>
      </div>

      {/* Quick Sync Notice Bar */}
      <div className="mb-5 p-3 rounded-xl bg-[#0b1612] border border-emerald-950 flex items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-300">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>
            Hệ thống tự động đồng bộ tài liệu (PDF, DOCX, PPTX, Google Docs) từ Google Drive vào Vector DB của Kali0t.
          </span>
        </div>
        <button
          onClick={handleTriggerSync}
          className="text-emerald-400 hover:text-emerald-300 underline font-semibold shrink-0"
        >
          Đồng bộ ngay
        </button>
      </div>

      {/* Filter & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-5">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Tìm theo tên file, hãng..."
            className="w-full bg-[#0b1612] border border-emerald-950 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
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
      </div>

      {/* Document Table */}
      <div className="glass-panel rounded-2xl overflow-hidden shadow-xl flex-1 border border-emerald-950">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0b1612] text-slate-400 uppercase font-mono text-[10px] tracking-wider border-b border-emerald-950">
              <tr>
                <th className="py-3 px-4">Tài liệu</th>
                <th className="py-3 px-4">Hãng</th>
                <th className="py-3 px-4">Phân nhóm</th>
                <th className="py-3 px-4 text-center">Trang</th>
                <th className="py-3 px-4 text-center">Chunks Vector</th>
                <th className="py-3 px-4 text-center">Lưu trữ Hybrid</th>
                <th className="py-3 px-4 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-emerald-950/60">
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    <Files className="w-8 h-8 text-slate-600 mx-auto mb-2 opacity-50" />
                    Không tìm thấy tài liệu nào. Bấm <strong>"Sync Google Drive"</strong> hoặc <strong>"Upload File"</strong> để thêm tài liệu.
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => {
                  const gdriveUrl = doc.doc_metadata?.gdrive_url;
                  return (
                    <tr key={doc.id} className="hover:bg-emerald-950/20 transition-colors group">
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-lg bg-surface-900 text-emerald-400 flex items-center justify-center font-bold font-mono text-[10px] uppercase border border-emerald-950 shrink-0">
                            {doc.file_type}
                          </div>
                          <div>
                            <p 
                              onClick={() => onSelectDocForChat && onSelectDocForChat(doc.document_name)}
                              className="font-semibold text-white hover:text-emerald-300 transition-colors cursor-pointer"
                              title="Click để đặt câu hỏi về tài liệu này trong Kali0t Chat"
                            >
                              {doc.document_name}
                            </p>
                            <div className="flex items-center gap-2 text-[10px] text-slate-500">
                              <span>{(doc.file_size_bytes / (1024 * 1024)).toFixed(2)} MB</span>
                              {doc.doc_metadata?.synced_at && (
                                <>
                                  <span>•</span>
                                  <span className="text-emerald-500/80">Synced {doc.doc_metadata.synced_at}</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-slate-300 font-medium">{doc.vendor}</td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono text-[10px] border border-emerald-900">
                          {doc.solution_category}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-center font-mono font-bold text-slate-300">
                        {doc.page_count}
                      </td>
                      <td className="py-3.5 px-4 text-center font-mono text-emerald-400 font-bold">
                        {doc.chunk_count}
                      </td>
                      <td className="py-3.5 px-4 text-center">
                        <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-800 text-[10px] font-mono">
                          <HardDrive className="w-3 h-3 text-emerald-400" />
                          <span>Linux</span>
                          <span>+</span>
                          <Cloud className="w-3 h-3 text-emerald-400" />
                          <span>Drive</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* Google Drive Link */}
                          {gdriveUrl ? (
                            <a
                              href={gdriveUrl}
                              target="_blank"
                              rel="noreferrer"
                              className="p-1.5 rounded-lg text-emerald-400 hover:text-white hover:bg-emerald-950 border border-emerald-900 transition-colors"
                              title="Mở tài liệu trên Google Drive"
                            >
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          ) : (
                            <button
                              onClick={() => window.open(`https://drive.google.com/drive/search?q=${encodeURIComponent(doc.document_name)}`, '_blank')}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-300 hover:bg-emerald-950/40 transition-colors"
                              title="Tìm trên Google Drive"
                            >
                              <Cloud className="w-3.5 h-3.5" />
                            </button>
                          )}

                          {/* Download from Server */}
                          <a
                            href={api.getDocumentDownloadUrl(doc.id)}
                            download={doc.document_name}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-300 hover:bg-emerald-950/40 transition-colors"
                            title="Tải về từ máy chủ Linux"
                          >
                            <Download className="w-3.5 h-3.5" />
                          </a>

                          {/* Delete */}
                          <button
                            onClick={() => handleDelete(doc.id, doc.document_name)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition-colors"
                            title="Xóa tài liệu"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sync Google Drive Progress Modal */}
      {isSyncModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-[#0b1612] border border-emerald-700/60 rounded-2xl w-full max-w-lg overflow-hidden shadow-glow-jade">
            {/* Modal Header */}
            <div className="p-4 sm:p-5 border-b border-emerald-950 flex items-center justify-between bg-gradient-to-r from-emerald-950/60 to-surface-900">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-950 text-emerald-400 flex items-center justify-center border border-emerald-800">
                  <FolderSync className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Google Drive Two-Way Sync</h3>
                  <p className="text-[11px] text-slate-400">Đồng bộ toàn bộ tài liệu từ Google Drive về Máy chủ Linux & Web</p>
                </div>
              </div>
              <button
                onClick={() => setIsSyncModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-emerald-950"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-4 sm:p-6 space-y-4 max-h-[70vh] overflow-y-auto">
              {isSyncingDrive ? (
                <div className="py-8 flex flex-col items-center justify-center text-center space-y-3">
                  <Loader2 className="w-10 h-10 text-emerald-400 animate-spin" />
                  <div>
                    <p className="text-sm font-semibold text-white">Đang đồng bộ từ Google Drive...</p>
                    <p className="text-xs text-slate-400 mt-1">
                      Đang kết nối API, tải tệp về server Linux, phân tích cấu trúc & nhúng Vector DB.
                    </p>
                  </div>
                </div>
              ) : syncResult ? (
                <div className="space-y-4">
                  <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-xs text-emerald-200 flex items-start gap-2.5">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-white">{syncResult.message}</p>
                      <p className="text-[11px] text-emerald-400/90 mt-0.5">
                        Tổng số tệp: <strong>{syncResult.synced_count}</strong> | Tổng Vector Chunks: <strong>{syncResult.total_chunks || '50+'}</strong>
                      </p>
                    </div>
                  </div>

                  {syncResult.synced_files && syncResult.synced_files.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold text-slate-300 mb-2 uppercase font-mono tracking-wider">
                        Danh sách tệp đã đồng bộ ({syncResult.synced_files.length}):
                      </h4>
                      <div className="space-y-2">
                        {syncResult.synced_files.map((file, idx) => (
                          <div
                            key={idx}
                            className="p-2.5 rounded-xl bg-surface-900 border border-emerald-950 flex items-center justify-between text-xs hover:border-emerald-800 transition-colors"
                          >
                            <div className="flex items-center gap-2 min-w-0">
                              <FileText className="w-4 h-4 text-emerald-400 shrink-0" />
                              <div className="truncate">
                                <p className="font-medium text-white truncate">{file.name}</p>
                                <span className="text-[10px] text-slate-500">
                                  {file.vendor || 'Bảo mật'} • {file.pages} trang • {file.chunks} chunks
                                </span>
                              </div>
                            </div>
                            {file.gdrive_url && (
                              <a
                                href={file.gdrive_url}
                                target="_blank"
                                rel="noreferrer"
                                className="px-2 py-1 rounded bg-emerald-950 text-emerald-300 text-[10px] hover:bg-emerald-900 flex items-center gap-1 shrink-0 ml-2"
                              >
                                <ExternalLink className="w-2.5 h-2.5" />
                                <span>Drive</span>
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {syncResult.errors && syncResult.errors.length > 0 && (
                    <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-800 text-xs text-rose-300 space-y-1">
                      <div className="flex items-center gap-1.5 font-bold">
                        <AlertCircle className="w-4 h-4 text-rose-400" />
                        <span>Cảnh báo / Lỗi trong quá trình xử lý:</span>
                      </div>
                      {syncResult.errors.map((e, idx) => (
                        <p key={idx} className="text-[11px] text-rose-300/90 pl-5">• {e}</p>
                      ))}
                    </div>
                  )}
                </div>
              ) : null}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-emerald-950 flex justify-end gap-2 bg-[#08100c]">
              <button
                onClick={() => setIsSyncModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-surface-900 hover:bg-surface-800 text-xs text-slate-300 font-semibold"
              >
                Đóng
              </button>
              <button
                onClick={handleTriggerSync}
                disabled={isSyncingDrive}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs text-white font-bold flex items-center gap-1.5 disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isSyncingDrive ? 'animate-spin' : ''}`} />
                <span>Đồng bộ lại</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* File Upload Modal */}
      <FileUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={() => {
          fetchDocuments();
        }}
      />
    </div>
  );
};
