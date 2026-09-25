import React, { useEffect, useState } from 'react';
import { Check, Loader2, Shield, Trash2, UserRound, Users, X } from 'lucide-react';
import { User, UserAdminUpdate } from '../../types';
import { api } from '../../services/api';

interface UserManagementProps {
  currentUser: User;
}

export const UserManagement: React.FC<UserManagementProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [busyUserId, setBusyUserId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState('');

  const loadUsers = async () => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      setUsers(await api.getUsers());
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Không thể tải danh sách người dùng.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const updateUser = async (userId: number, changes: UserAdminUpdate) => {
    setBusyUserId(userId);
    setErrorMessage('');
    try {
      const updated = await api.updateUser(userId, changes);
      setUsers((items) => items.map((item) => item.id === updated.id ? updated : item));
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Không thể cập nhật người dùng.');
    } finally {
      setBusyUserId(null);
    }
  };

  const deleteUser = async (user: User) => {
    if (!window.confirm(`Xóa tài khoản ${user.username}?`)) return;
    setBusyUserId(user.id);
    setErrorMessage('');
    try {
      await api.deleteUser(user.id);
      setUsers((items) => items.filter((item) => item.id !== user.id));
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Không thể xóa người dùng.');
    } finally {
      setBusyUserId(null);
    }
  };

  return (
    <section className="min-w-0 flex-1 overflow-y-auto bg-[#070b09] p-4 sm:p-6 md:p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-glow-jade">
              <Users className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white sm:text-xl">Quản lý người dùng</h2>
              <p className="text-xs text-slate-400">Phân quyền và kiểm soát trạng thái tài khoản Kali0t</p>
            </div>
          </div>
          <span className="rounded-lg border border-emerald-900 bg-emerald-950/60 px-3 py-1.5 text-xs font-mono text-emerald-300">
            {users.length} users
          </span>
        </div>

        {errorMessage && (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-rose-900/60 bg-rose-950/30 px-4 py-3 text-xs text-rose-300">
            <X className="h-4 w-4 shrink-0" />
            {errorMessage}
          </div>
        )}

        <div className="overflow-x-auto rounded-2xl border border-emerald-950 bg-[#0b1612]/80">
          {isLoading ? (
            <div className="flex items-center justify-center gap-2 p-12 text-sm text-emerald-300">
              <Loader2 className="h-4 w-4 animate-spin" /> Đang tải người dùng...
            </div>
          ) : (
            <table className="w-full min-w-[720px] text-left text-xs">
              <thead className="border-b border-emerald-950 bg-emerald-950/30 text-[10px] uppercase tracking-wider text-emerald-500">
                <tr>
                  <th className="px-4 py-3">Người dùng</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Trạng thái</th>
                  <th className="px-4 py-3 text-right">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-emerald-950/70">
                {users.map((user) => {
                  const isBusy = busyUserId === user.id;
                  const isSelf = user.id === currentUser.id;
                  return (
                    <tr key={user.id} className="text-slate-300 hover:bg-emerald-950/20">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2.5">
                          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-emerald-800 bg-emerald-950 text-emerald-300">
                            {user.role === 'admin' ? <Shield className="h-4 w-4" /> : <UserRound className="h-4 w-4" />}
                          </div>
                          <div>
                            <p className="font-semibold text-slate-100">{user.full_name || user.username}</p>
                            <p className="text-[11px] text-slate-500">@{user.username}{isSelf ? ' · Bạn' : ''}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-slate-400">{user.email}</td>
                      <td className="px-4 py-3">
                        <select
                          value={user.role}
                          disabled={isBusy || isSelf}
                          onChange={(event) => updateUser(user.id, { role: event.target.value as 'admin' | 'user' })}
                          className="rounded-lg border border-emerald-900 bg-[#09110d] px-2 py-1.5 text-xs text-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <option value="user">User</option>
                          <option value="admin">Admin</option>
                        </select>
                      </td>
                      <td className="px-4 py-3">
                        <button
                          disabled={isBusy || isSelf}
                          onClick={() => updateUser(user.id, { is_active: !user.is_active })}
                          className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold disabled:cursor-not-allowed disabled:opacity-50 ${
                            user.is_active
                              ? 'border-emerald-800 bg-emerald-950/70 text-emerald-300'
                              : 'border-slate-700 bg-slate-900 text-slate-400'
                          }`}
                        >
                          {user.is_active ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
                          {user.is_active ? 'Hoạt động' : 'Đã khóa'}
                        </button>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          disabled={isBusy || isSelf}
                          onClick={() => deleteUser(user)}
                          title={isSelf ? 'Không thể xóa tài khoản đang sử dụng' : 'Xóa người dùng'}
                          className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-rose-950/40 hover:text-rose-300 disabled:cursor-not-allowed disabled:opacity-30"
                        >
                          {isBusy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </section>
  );
};
