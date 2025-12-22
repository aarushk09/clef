'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { CheckCircle, XCircle, Loader2, Mail, RefreshCw, Shield } from 'lucide-react';
import Link from 'next/link';
import { toast } from 'sonner';

function CLICallbackContent() {
  const searchParams = useSearchParams();
  const [step, setStep] = useState<'checking' | '2fa-required' | 'init' | 'otp-sent' | 'verifying' | 'success' | 'error'>('checking');
  const [message, setMessage] = useState('');
  const [otp, setOtp] = useState('');
  const [sendingOTP, setSendingOTP] = useState(false);
  const [verifyingOTP, setVerifyingOTP] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [error, setError] = useState('');

  const token = searchParams.get('token');
  const userId = searchParams.get('userId');

  useEffect(() => {
    if (!token || !userId) {
      setStep('error');
      setMessage('Missing authentication parameters');
      return;
    }

    const check2FAStatus = async () => {
      const jwtToken = localStorage.getItem('token');
      if (!jwtToken) {
        // Not logged in, redirect to login
        window.location.href = `/auth/login?cli=true&token=${token}`;
        return;
      }

      try {
        const response = await fetch('/api/user/stats', {
          headers: {
            'Authorization': `Bearer ${jwtToken}`
          }
        });
        const data = await response.json();

        if (data.success) {
          if (data.stats.is2FAEnabled) {
            setStep('init');
          } else {
            setStep('2fa-required');
          }
        } else {
          setStep('error');
          setMessage('Failed to verify account status');
        }
      } catch (error) {
        setStep('error');
        setMessage('Failed to verify account status');
      }
    };

    check2FAStatus();
  }, [token, userId]);

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const sendOTP = async () => {
    if (!token || !userId) return;

    setSendingOTP(true);
    setError('');

    try {
      // Get JWT token from localStorage
      const jwtToken = localStorage.getItem('token');
      if (!jwtToken) {
        setError('Please login first');
        setStep('error');
        return;
      }

      const response = await fetch('/api/auth/cli-otp/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${jwtToken}`,
        },
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStep('otp-sent');
        setMessage('OTP sent to your email');
        setResendCooldown(60); // 60 second cooldown
        toast.success('OTP sent to your email');
      } else {
        if (response.status === 429) {
          setResendCooldown(data.retryAfter || 60);
          setError(`Please wait ${data.retryAfter || 60} seconds before requesting another OTP`);
        } else {
          setError(data.error || 'Failed to send OTP');
        }
        toast.error(data.error || 'Failed to send OTP');
      }
    } catch (error: any) {
      setError('Failed to send OTP: ' + error.message);
      toast.error('Failed to send OTP');
    } finally {
      setSendingOTP(false);
    }
  };

  const verifyOTP = async () => {
    if (!otp || otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    if (!token || !userId) return;

    setVerifyingOTP(true);
    setError('');

    try {
      const jwtToken = localStorage.getItem('token');
      if (!jwtToken) {
        setError('Please login first');
        setStep('error');
        return;
      }

      const response = await fetch('/api/auth/cli-otp/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${jwtToken}`,
        },
        body: JSON.stringify({ otp }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStep('success');
        setMessage('Successfully authenticated! You may go back to the command line.');
        toast.success('Authentication successful!');
      } else {
        setError(data.error || 'Invalid OTP');
        if (data.attemptsRemaining !== undefined) {
          setError(`${data.error} (${data.attemptsRemaining} attempts remaining)`);
        }
        toast.error(data.error || 'Invalid OTP');
        setOtp(''); // Clear OTP on error
      }
    } catch (error: any) {
      setError('Failed to verify OTP: ' + error.message);
      toast.error('Failed to verify OTP');
      setOtp('');
    } finally {
      setVerifyingOTP(false);
    }
  };

  const handleOTPChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setOtp(value);
    setError('');
  };

  if (!token || !userId) {
    return (
      <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center p-4">
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-8 max-w-md w-full">
          <div className="text-center">
            <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Invalid Request</h2>
            <p className="text-[#888]">Missing authentication parameters</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center p-4">
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-8 max-w-md w-full">
        {step === 'checking' && (
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-[#4a9eff] animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Verifying Security...</h2>
          </div>
        )}

        {step === '2fa-required' && (
          <div className="text-center">
             <div className="w-16 h-16 bg-yellow-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-yellow-500" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">2FA Required</h2>
            <p className="text-[#888] mb-6">
              To use the CLI, you must enable Two-Factor Authentication on your account for added security.
            </p>
            <Link
              href="/dashboard/settings"
              className="block w-full bg-[#4a9eff] hover:bg-[#3a8eef] text-white font-medium py-3 px-4 rounded-lg transition-colors text-center"
            >
              Go to Settings
            </Link>
          </div>
        )}

        {step === 'init' && (
          <div className="text-center">
            <div className="w-16 h-16 bg-[#4a9eff]/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-[#4a9eff]" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">CLI Authentication</h2>
            <p className="text-[#888] mb-6">
              Click the button below to receive a one-time password (OTP) via email to authenticate your CLI.
            </p>
            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
            <button
              onClick={sendOTP}
              disabled={sendingOTP}
              className="w-full bg-[#4a9eff] hover:bg-[#3a8eef] text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {sendingOTP ? (
                <>
                  <Loader2 className="w-4 h-4 inline-block mr-2 animate-spin" />
                  Sending OTP...
                </>
              ) : (
                'Authenticate'
              )}
            </button>
          </div>
        )}

        {step === 'otp-sent' && (
          <div>
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-[#4a9eff]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mail className="w-8 h-8 text-[#4a9eff]" />
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">Check Your Email</h2>
              <p className="text-[#888] text-sm">
                We've sent a 6-digit OTP to your email address. It will expire in 10 minutes.
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-[#e0e0e0] mb-2">
                Enter OTP
              </label>
              <input
                type="text"
                value={otp}
                onChange={handleOTPChange}
                placeholder="000000"
                maxLength={6}
                className="w-full bg-[#0f0f0f] border border-[#2a2a2a] rounded-lg px-4 py-3 text-white text-center text-2xl font-mono tracking-widest focus:outline-none focus:border-[#4a9eff] transition-colors"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && otp.length === 6) {
                    verifyOTP();
                  }
                }}
              />
            </div>

            <button
              onClick={verifyOTP}
              disabled={verifyingOTP || otp.length !== 6}
              className="w-full bg-[#4a9eff] hover:bg-[#3a8eef] text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 mb-3"
            >
              {verifyingOTP ? (
                <>
                  <Loader2 className="w-4 h-4 inline-block mr-2 animate-spin" />
                  Verifying...
                </>
              ) : (
                'Verify OTP'
              )}
            </button>

            <button
              onClick={sendOTP}
              disabled={sendingOTP || resendCooldown > 0}
              className="w-full bg-[#1a1a1a] hover:bg-[#2a2a2a] border border-[#2a2a2a] text-[#e0e0e0] font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 flex items-center justify-center"
            >
              {resendCooldown > 0 ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Resend in {resendCooldown}s
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Resend OTP
                </>
              )}
            </button>
          </div>
        )}

        {step === 'success' && (
          <div className="text-center">
            <CheckCircle className="w-16 h-16 text-[#4a9eff] mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Success!</h2>
            <p className="text-[#888] mb-4">{message}</p>
            <p className="text-sm text-[#666]">
              You can now go back to your command line and continue using the CLI.
            </p>
          </div>
        )}

        {step === 'error' && (
          <div className="text-center">
            <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Authentication Failed</h2>
            <p className="text-[#888]">{message || error}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function CLICallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center p-4">
        <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg p-8 max-w-md w-full text-center">
          <Loader2 className="w-12 h-12 text-[#4a9eff] animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Loading...</h2>
        </div>
      </div>
    }>
      <CLICallbackContent />
    </Suspense>
  );
}
