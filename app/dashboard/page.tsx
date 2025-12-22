'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  Key, 
  Activity, 
  CreditCard, 
  Settings, 
  LogOut, 
  Plus,
  Eye,
  Trash2,
  Copy,
  Terminal,
  RefreshCw,
  BookOpen,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import Link from 'next/link';

interface ApiKey {
  id: string;
  key: string;
  name: string;
  createdAt: string;
  usageCount: number;
  isActive: boolean;
}

interface User {
  id: string;
  name: string;
  email: string;
  credits: number;
}

interface Stats {
  credits: number;
  totalRequests: number;
  requestsToday: number;
  creditsUsedToday: number;
  avgResponseTime: string;
  is2FAEnabled?: boolean;
  twoFactorMethod?: string | null;
}

interface ApiLog {
  id: string;
  endpoint: string;
  method: string;
  statusCode: number;
  timestamp: string;
  creditsUsed: number;
  processingTime: number;
  apiKeyId: string;
}

function DashboardContent() {
  const [user, setUser] = useState<User | null>(null);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [stats, setStats] = useState<Stats>({
    credits: 0,
    totalRequests: 0,
    requestsToday: 0,
    creditsUsedToday: 0,
    avgResponseTime: '0s',
    is2FAEnabled: false,
    twoFactorMethod: null
  });
  const [logs, setLogs] = useState<ApiLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewKeyForm, setShowNewKeyForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [creatingKey, setCreatingKey] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [authorizingCLI, setAuthorizingCLI] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const showCLIPrompt = searchParams.get('cli') === 'true';

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (!token || !userData) {
      router.push('/auth/login');
      return;
    }

    setUser(JSON.parse(userData));
    
    const fetchData = async () => {
      await Promise.all([loadApiKeys(), loadStats(), loadLogs()]);
      setLoading(false);
    };

    fetchData();
  }, [router]);

  const loadApiKeys = async () => {
    try {
      const response = await fetch('/api/keys/list', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      if (data.success) {
        setApiKeys(data.apiKeys);
      }
    } catch (error) {
      console.error('Error loading API keys:', error);
      toast.error('Failed to load API keys');
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/user/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
        if (data.stats.credits !== undefined) {
          const userData = localStorage.getItem('user');
          if (userData) {
            const parsed = JSON.parse(userData);
            parsed.credits = data.stats.credits;
            localStorage.setItem('user', JSON.stringify(parsed));
            setUser(parsed);
          }
        }
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadLogs = async () => {
    try {
      const response = await fetch('/api/user/logs?limit=10', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      if (data.success) {
        setLogs(data.logs);
      }
    } catch (error) {
      console.error('Error loading logs:', error);
    }
  };

  const authorizeCLI = async () => {
    setAuthorizingCLI(true);
    try {
      const response = await fetch('/api/auth/cli-callback', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      const data = await response.json();
      if (data.success) {
        // Redirect to callback page for OTP authentication
        router.push(data.url);
      } else {
        toast.error(data.error || 'Failed to authorize CLI');
        setAuthorizingCLI(false);
      }
    } catch (error) {
      console.error('Error authorizing CLI:', error);
      toast.error('Failed to authorize CLI');
      setAuthorizingCLI(false);
    }
  };

  const createApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingKey(true);

    try {
      const response = await fetch('/api/keys/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ 
          userId: user?.id, 
          name: newKeyName 
        }),
      });

      const data = await response.json();

      if (data.success) {
        setApiKeys([data.apiKey, ...apiKeys]);
        setNewKeyName('');
        setShowNewKeyForm(false);
        loadStats();
        toast.success('API key created successfully');
      } else {
        toast.error(data.error || 'Failed to create API key');
      }
    } catch (error) {
      console.error('Error creating API key:', error);
      toast.error('Failed to create API key');
    } finally {
      setCreatingKey(false);
    }
  };

  const deleteApiKey = async (id: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`/api/keys/delete?id=${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      const data = await response.json();

      if (data.success || response.ok) {
        setApiKeys(apiKeys.filter(key => key.id !== id));
        toast.success('API key deleted');
      } else {
        toast.error(data.error || 'Failed to delete API key');
      }
    } catch (error) {
      console.error('Error deleting API key:', error);
      toast.error('Failed to delete API key');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/');
    toast.info('Logged out successfully');
  };

  const refreshData = async () => {
    setRefreshing(true);
    await Promise.all([loadApiKeys(), loadStats(), loadLogs()]);
    setRefreshing(false);
    toast.success('Dashboard updated');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f0f0f] text-[#e0e0e0] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-2 border-[#2a2a2a] border-t-[#4a9eff] mx-auto mb-4"></div>
          <p className="text-[#888]">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] text-[#e0e0e0]">
      {/* Header */}
      <header className="border-b border-[#2a2a2a] bg-[#0f0f0f] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-white">EdPear Dashboard</h1>
              <button 
                onClick={refreshData}
                disabled={refreshing}
                className="flex items-center space-x-1 text-sm px-3 py-1.5 bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#2a2a2a] rounded-lg transition-colors disabled:opacity-50 text-[#888]"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
                <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
              </button>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-[#888]">{user?.name}</span>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-1.5 bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#2a2a2a] rounded-lg transition-colors text-sm text-[#888]"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </header>

        {/* 2FA Banner */}
        {!loading && !stats.is2FAEnabled && (
          <div className="bg-[#1a1a00] border-b border-yellow-900/30 text-yellow-200 px-6 py-3">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-1 bg-yellow-900/50 rounded-full">
                  <Activity className="w-4 h-4 text-yellow-500" />
                </div>
                <p className="text-sm">
                  <span className="font-semibold">Developer Account Notice:</span> Two-Factor Authentication (2FA) is required for advanced features like CLI access.
                </p>
              </div>
              <Link 
                href="/dashboard/settings"
                className="text-xs font-medium bg-yellow-900/40 hover:bg-yellow-900/60 border border-yellow-900/50 px-3 py-1.5 rounded-lg transition-colors flex items-center space-x-1"
              >
                <span>Enable 2FA</span>
                <Plus className="w-3 h-3" />
              </Link>
            </div>
          </div>
        )}

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* CLI Authorization Prompt */}
        {showCLIPrompt && (
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <Terminal className="w-6 h-6 text-[#4a9eff] mt-0.5" />
                <div>
                  <h3 className="text-lg font-medium text-white mb-2">Authorize CLI Access</h3>
                  <p className="text-[#888] mb-4">
                    Click the button below to authorize your CLI. This will generate a temporary token for authentication.
                  </p>
                  <button
                    onClick={authorizeCLI}
                    disabled={authorizingCLI}
                    className="px-4 py-2 bg-[#4a9eff] hover:bg-[#3a8eef] text-white rounded-lg transition-colors disabled:opacity-50 text-sm font-medium"
                  >
                    {authorizingCLI ? 'Authorizing...' : 'Authorize CLI'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#888] mb-1">Remaining Credits</p>
                <p className="text-3xl font-semibold text-white">{stats.credits}</p>
              </div>
              <CreditCard className="w-8 h-8 text-[#4a9eff]" />
            </div>
          </div>
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#888] mb-1">Active API Keys</p>
                <p className="text-3xl font-semibold text-white">{apiKeys.length}</p>
              </div>
              <Key className="w-8 h-8 text-[#4a9eff]" />
            </div>
          </div>
          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[#888] mb-1">Total Requests</p>
                <p className="text-3xl font-semibold text-white">{stats.totalRequests}</p>
              </div>
              <Activity className="w-8 h-8 text-[#4a9eff]" />
            </div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - API Logs */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg overflow-hidden">
              <div className="p-6 border-b border-[#2a2a2a] flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <Terminal className="w-5 h-5 text-[#888]" />
                  <h2 className="text-lg font-semibold text-white">Recent API Logs</h2>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-[#0f0f0f] text-[#888] uppercase text-xs">
                    <tr>
                      <th className="px-6 py-3 text-left">Status</th>
                      <th className="px-6 py-3 text-left">Endpoint</th>
                      <th className="px-6 py-3 text-left">Time</th>
                      <th className="px-6 py-3 text-left">Latency</th>
                      <th className="px-6 py-3 text-left">Cost</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#2a2a2a]">
                    {logs.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-8 text-center text-[#888]">
                          No requests found yet. Make your first API call to see logs here.
                        </td>
                      </tr>
                    ) : (
                      logs.map((log) => (
                        <tr key={log.id} className="hover:bg-[#0f0f0f] transition-colors">
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              log.statusCode >= 200 && log.statusCode < 300 
                                ? 'bg-[#1a3a2a] text-[#4ade80]' 
                                : 'bg-[#3a1a1a] text-[#f87171]'
                            }`}>
                              {log.statusCode}
                            </span>
                          </td>
                          <td className="px-6 py-4 font-mono text-[#e0e0e0] text-xs">
                            {log.method} {log.endpoint}
                          </td>
                          <td className="px-6 py-4 text-[#888] text-xs">
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-[#888] text-xs">
                            {log.processingTime}ms
                          </td>
                          <td className="px-6 py-4 text-[#888] text-xs">
                            {log.creditsUsed} credits
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* API Keys Section */}
            <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg">
              <div className="p-6 border-b border-[#2a2a2a]">
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <Key className="w-5 h-5 text-[#888]" />
                    <h2 className="text-lg font-semibold text-white">API Keys</h2>
                  </div>
                  <button
                    onClick={() => setShowNewKeyForm(true)}
                    className="flex items-center space-x-2 px-4 py-2 bg-[#4a9eff] hover:bg-[#3a8eef] text-white rounded-lg transition-colors text-sm font-medium"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Create New Key</span>
                  </button>
                </div>
              </div>

              {showNewKeyForm && (
                <div className="p-6 border-b border-[#2a2a2a] bg-[#0f0f0f]">
                  <form onSubmit={createApiKey} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-white mb-2">
                        Key Name
                      </label>
                      <input
                        type="text"
                        value={newKeyName}
                        onChange={(e) => setNewKeyName(e.target.value)}
                        className="w-full px-4 py-2 bg-[#0f0f0f] border border-[#2a2a2a] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4a9eff] focus:border-transparent transition-all text-white"
                        placeholder="e.g., Production Key"
                        required
                      />
                    </div>
                    <div className="flex space-x-3">
                      <button
                        type="submit"
                        disabled={creatingKey}
                        className="px-4 py-2 bg-[#4a9eff] hover:bg-[#3a8eef] text-white rounded-lg font-medium transition-colors disabled:opacity-50 text-sm"
                      >
                        {creatingKey ? 'Creating...' : 'Create Key'}
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowNewKeyForm(false)}
                        className="px-4 py-2 border border-[#2a2a2a] text-[#888] rounded-lg font-medium hover:bg-[#1a1a1a] transition-colors text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              )}

              <div className="p-6">
                {apiKeys.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-[#888]">No API keys found</p>
                    <p className="text-sm text-[#666] mt-1">Generate your first API key to get started</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {apiKeys.map((key) => (
                      <div key={key.id} className="flex items-center justify-between p-4 bg-[#0f0f0f] border border-[#2a2a2a] rounded-lg hover:border-[#3a3a3a] transition-all">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-medium text-white">{key.name}</h3>
                            <span className={`text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider ${
                              key.isActive ? 'bg-[#1a3a2a] text-[#4ade80]' : 'bg-[#3a1a1a] text-[#f87171]'
                            }`}>
                              {key.isActive ? 'Active' : 'Inactive'}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <code className="text-xs bg-[#0f0f0f] px-2 py-1 rounded text-[#888] font-mono border border-[#2a2a2a]">
                              {key.key}
                            </code>
                            <button
                              onClick={() => copyToClipboard(key.key)}
                              className="p-1 text-[#888] hover:text-white transition-colors"
                              title="Copy key"
                            >
                              <Copy className="w-3 h-3" />
                            </button>
                          </div>
                          <p className="text-xs text-[#666] mt-2">
                            {key.usageCount} requests • Created {new Date(key.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                        <button
                          onClick={() => deleteApiKey(key.id)}
                          className="p-2 text-[#888] hover:text-[#f87171] transition-colors ml-4"
                          title="Delete key"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
              <h3 className="font-semibold text-white mb-4 flex items-center space-x-2">
                <Activity className="w-4 h-4 text-[#888]" />
                <span>Today's Activity</span>
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-[#0f0f0f] rounded-lg border border-[#2a2a2a]">
                  <span className="text-sm text-[#888]">Requests</span>
                  <span className="font-mono font-medium text-white">{stats.requestsToday}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-[#0f0f0f] rounded-lg border border-[#2a2a2a]">
                  <span className="text-sm text-[#888]">Credits Used</span>
                  <span className="font-mono font-medium text-white">{stats.creditsUsedToday}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-[#0f0f0f] rounded-lg border border-[#2a2a2a]">
                  <span className="text-sm text-[#888]">Avg Latency</span>
                  <span className="font-mono font-medium text-white">{stats.avgResponseTime}</span>
                </div>
              </div>
            </div>

            <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-6">
              <h3 className="font-semibold text-white mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <Link 
                  href="/docs"
                  className="w-full text-left p-3 bg-[#0f0f0f] rounded-lg hover:bg-[#1a1a1a] transition-colors border border-transparent hover:border-[#2a2a2a] group flex items-center space-x-3"
                >
                  <div className="p-2 bg-[#1a1a1a] rounded-lg group-hover:bg-[#2a2a2a] transition-colors">
                    <BookOpen className="w-4 h-4 text-[#4a9eff]" />
                  </div>
                  <div>
                    <p className="font-medium text-sm text-white">Documentation</p>
                    <p className="text-xs text-[#888]">View integration guides</p>
                  </div>
                </Link>
                <button className="w-full text-left p-3 bg-[#0f0f0f] rounded-lg hover:bg-[#1a1a1a] transition-colors border border-transparent hover:border-[#2a2a2a] group flex items-center space-x-3">
                  <div className="p-2 bg-[#1a1a1a] rounded-lg group-hover:bg-[#2a2a2a] transition-colors">
                    <Eye className="w-4 h-4 text-[#4a9eff]" />
                  </div>
                  <div>
                    <p className="font-medium text-sm text-white">Test Vision API</p>
                    <p className="text-xs text-[#888]">Try our image analysis</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#4a9eff] animate-spin" />
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
