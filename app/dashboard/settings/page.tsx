'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Shield, 
  Smartphone, 
  Mail, 
  Check, 
  AlertTriangle,
  ArrowLeft,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import Link from 'next/link';

interface User {
  id: string;
  name: string;
  email: string;
  credits: number;
  is2FAEnabled?: boolean;
  twoFactorMethod?: 'email' | 'passkey' | null;
}

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/auth/login');
      return;
    }

    // Load fresh user stats to get 2FA status
    fetch('/api/user/stats', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // Merge with local user data
        const localUser = JSON.parse(localStorage.getItem('user') || '{}');
        setUser({
          ...localUser,
          is2FAEnabled: data.stats.is2FAEnabled,
          twoFactorMethod: data.stats.twoFactorMethod
        });
      }
    })
    .catch(err => console.error(err))
    .finally(() => setLoading(false));
  }, [router]);

  const enable2FA = async (method: 'email' | 'passkey') => {
    setUpdating(true);
    try {
      const response = await fetch('/api/user/2fa/enable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ method })
      });

      const data = await response.json();

      if (data.success) {
        setUser(prev => prev ? ({ ...prev, is2FAEnabled: true, twoFactorMethod: method }) : null);
        toast.success(`Two-factor authentication enabled via ${method}`);
      } else {
        toast.error(data.error || 'Failed to enable 2FA');
      }
    } catch (error) {
      toast.error('Failed to update settings');
    } finally {
      setUpdating(false);
    }
  };

  const disable2FA = async () => {
    if (!confirm('Are you sure you want to disable 2FA? This will reduce your account security and disable CLI access.')) {
      return;
    }

    setUpdating(true);
    try {
      const response = await fetch('/api/user/2fa/disable', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const data = await response.json();

      if (data.success) {
        setUser(prev => prev ? ({ ...prev, is2FAEnabled: false, twoFactorMethod: null }) : null);
        toast.success('Two-factor authentication disabled');
      } else {
        toast.error(data.error || 'Failed to disable 2FA');
      }
    } catch (error) {
      toast.error('Failed to update settings');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#4a9eff] animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] text-[#e0e0e0]">
      <header className="border-b border-[#2a2a2a] bg-[#0f0f0f] sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard" className="p-2 hover:bg-[#1a1a1a] rounded-lg transition-colors text-[#888]">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-xl font-semibold text-white">Account Settings</h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8 space-y-8">
        {/* Security Section */}
        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-medium text-white mb-1">Security</h2>
            <p className="text-[#888] text-sm">Manage your account security and authentication methods.</p>
          </div>

          <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg overflow-hidden">
            <div className="p-6 border-b border-[#2a2a2a]">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  <div className={`p-2 rounded-lg ${user?.is2FAEnabled ? 'bg-green-900/20' : 'bg-yellow-900/20'}`}>
                    <Shield className={`w-6 h-6 ${user?.is2FAEnabled ? 'text-green-500' : 'text-yellow-500'}`} />
                  </div>
                  <div>
                    <h3 className="text-base font-medium text-white mb-1">Two-Factor Authentication (2FA)</h3>
                    <p className="text-[#888] text-sm mb-3">
                      Add an extra layer of security to your account. Required for CLI access.
                    </p>
                    {user?.is2FAEnabled ? (
                      <div className="flex items-center space-x-2 text-green-500 text-sm bg-green-900/10 px-2 py-1 rounded w-fit">
                        <Check className="w-4 h-4" />
                        <span>Enabled via {user.twoFactorMethod === 'passkey' ? 'Google Passkey' : 'Email OTP'}</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-yellow-500 text-sm bg-yellow-900/10 px-2 py-1 rounded w-fit">
                        <AlertTriangle className="w-4 h-4" />
                        <span>Not Enabled</span>
                      </div>
                    )}
                  </div>
                </div>
                {user?.is2FAEnabled && (
                  <button
                    onClick={disable2FA}
                    disabled={updating}
                    className="px-4 py-2 border border-red-900/30 text-red-500 hover:bg-red-900/10 rounded-lg text-sm font-medium transition-colors"
                  >
                    Disable
                  </button>
                )}
              </div>
            </div>

            {!user?.is2FAEnabled && (
              <div className="p-6 bg-[#0f0f0f] space-y-4">
                {/* Google Passkey Option */}
                <div className="flex items-center justify-between p-4 border border-[#2a2a2a] rounded-lg hover:border-[#4a9eff] transition-colors group cursor-pointer"
                     onClick={() => enable2FA('passkey')}>
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-[#1a1a1a] rounded-lg group-hover:bg-[#2a2a2a]">
                      <Smartphone className="w-5 h-5 text-[#4a9eff]" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-white">Google Passkey (Recommended)</h4>
                      <p className="text-xs text-[#888]">Use your device's biometric or security key.</p>
                    </div>
                  </div>
                  <button disabled={updating} className="text-[#4a9eff] text-sm font-medium">
                    Enable
                  </button>
                </div>

                {/* Email OTP Option */}
                <div className="flex items-center justify-between p-4 border border-[#2a2a2a] rounded-lg hover:border-[#4a9eff] transition-colors group cursor-pointer"
                     onClick={() => enable2FA('email')}>
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-[#1a1a1a] rounded-lg group-hover:bg-[#2a2a2a]">
                      <Mail className="w-5 h-5 text-[#4a9eff]" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-white">Email OTP</h4>
                      <p className="text-xs text-[#888]">Receive a temporary code via email.</p>
                    </div>
                  </div>
                  <button disabled={updating} className="text-[#4a9eff] text-sm font-medium">
                    Enable
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

