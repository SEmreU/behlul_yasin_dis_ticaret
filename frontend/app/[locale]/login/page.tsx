'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import Link from 'next/link';

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '';

export default function LoginPage() {
  const { login, googleLogin } = useAuth();
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [loading, setLoading] = useState(false);
  const [gLoading, setGLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    if (!user || !pass) return;
    setError('');
    setLoading(true);
    try {
      await login({ email: user, password: pass });
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Giriş başarısız. Lütfen tekrar deneyin.';
      setError(errorMsg);
      setLoading(false);
    }
  };

  const handleGoogleResponse = useCallback(async (response: { credential: string }) => {
    setGLoading(true);
    setError('');
    try {
      await googleLogin(response.credential);
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Google ile giriş başarısız.';
      setError(errorMsg);
    } finally {
      setGLoading(false);
    }
  }, [googleLogin]);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return;
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      window.google?.accounts?.id?.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
      });
      window.google?.accounts?.id?.renderButton(
        document.getElementById('google-signin-btn'),
        { theme: 'filled_black', size: 'large', width: 360, text: 'signin_with', locale: 'tr' }
      );
    };
    document.body.appendChild(script);
    return () => { document.body.removeChild(script); };
  }, [handleGoogleResponse]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#040d1a] via-[#0a1628] to-[#0d1f35] font-['Outfit',sans-serif] relative overflow-hidden">
      {/* Animated Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 rounded-full bg-[#00e5a0] opacity-15 animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${3 + Math.random() * 4}s`,
            }}
          />
        ))}
      </div>

      {/* Login Card */}
      <div className="w-[400px] p-12 bg-gradient-to-br from-[#0d1f3588] to-[#0a162888] border border-[#1e3a5f] rounded-[20px] backdrop-blur-[20px] relative z-10">
        {/* Logo */}
        <div className="text-center mb-9">
          <div className="mb-3 flex justify-center">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <path d="M24 4L42 14V34L24 44L6 34V14L24 4Z" fill="url(#grad1)" opacity="0.9" />
              <path d="M24 4L42 14V34L24 44L6 34V14L24 4Z" stroke="#00e5a0" strokeWidth="1.5" fill="none" />
              <circle cx="24" cy="24" r="8" fill="#0a1628" stroke="#00e5a0" strokeWidth="1.5" />
              <circle cx="24" cy="24" r="3" fill="#00e5a0" />
              <defs>
                <linearGradient id="grad1" x1="6" y1="4" x2="42" y2="44">
                  <stop offset="0%" stopColor="#0a1628" />
                  <stop offset="100%" stopColor="#132744" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 className="text-[28px] font-bold text-[#e2e8f0] m-0 tracking-tight">TradeRadar</h1>
          <p className="text-sm text-[#64748b] mt-1.5 tracking-widest uppercase">Dış Ticaret İstihbarat Platformu</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-5 p-3 bg-[#ef444422] border border-[#ef4444] rounded-lg text-sm text-[#ef4444] flex items-start gap-2">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Username Input */}
        <div className="mb-5">
          <label className="block text-xs font-medium text-[#94a3b8] mb-2 uppercase tracking-wider">
            Kullanıcı Adı
          </label>
          <input
            className="w-full px-4 py-3.5 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-[15px] outline-none transition-all focus:border-[#00e5a066]"
            placeholder="kullanici@firma.com"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
          />
        </div>

        {/* Password Input */}
        <div className="mb-5">
          <label className="block text-xs font-medium text-[#94a3b8] mb-2 uppercase tracking-wider">
            Şifre
          </label>
          <input
            className="w-full px-4 py-3.5 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-[15px] outline-none transition-all focus:border-[#00e5a066]"
            type="password"
            placeholder="••••••••"
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
          />
        </div>

        {/* Login Button */}
        <button
          onClick={handleLogin}
          disabled={loading || !user || !pass}
          className="w-full px-4 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-lg text-[#0a1628] text-base font-semibold cursor-pointer flex items-center justify-center min-h-[48px] mt-2 disabled:opacity-50 disabled:cursor-not-allowed hover:brightness-110 transition-all"
        >
          {loading ? (
            <span className="w-5 h-5 border-[2.5px] border-[#0a162844] border-t-[#0a1628] rounded-full animate-spin" />
          ) : (
            'Giriş Yap'
          )}
        </button>

        {/* Google Sign-In Button */}
        {GOOGLE_CLIENT_ID && (
          <div className="mt-4">
            <div className="flex items-center gap-3 my-4">
              <div className="flex-1 h-px bg-[#1e3a5f]" />
              <span className="text-xs text-[#475569]">veya</span>
              <div className="flex-1 h-px bg-[#1e3a5f]" />
            </div>
            <div id="google-signin-btn" className="flex justify-center" />
            {gLoading && (
              <p className="text-center text-xs text-[#64748b] mt-2">Giriş yapılıyor...</p>
            )}
          </div>
        )}

        {/* Footer */}
        <div>
          <p className="text-center text-[13px] text-[#475569] mt-5">
            Erişim için yöneticinizle iletişime geçin
          </p>
          <div className="flex items-center gap-3 my-4">
            <div className="flex-1 h-px bg-[#1e3a5f]" />
            <span className="text-xs text-[#475569]">veya</span>
            <div className="flex-1 h-px bg-[#1e3a5f]" />
          </div>
          <p className="text-center text-[13px] text-[#64748b]">
            Hesabın yok mu?{' '}
            <Link href="/tr/register" className="text-[#00e5a0] font-semibold hover:text-[#00ffa8] transition-colors">
              Kayıt Ol
            </Link>
          </p>
        </div>
      </div>

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        @keyframes float {
          0%, 100% { transform: translateY(0) scale(1); opacity: 0.15; }
          50% { transform: translateY(-20px) scale(1.5); opacity: 0.3; }
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        
        .animate-float {
          animation: float 4s ease-in-out infinite;
        }
        
        .animate-spin {
          animation: spin 0.6s linear infinite;
        }
      `}</style>
    </div>
  );
}
