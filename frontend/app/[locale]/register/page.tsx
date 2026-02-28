'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/contexts/AuthContext';
import Link from 'next/link';

export default function RegisterPage() {
  const { register } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [pass, setPass] = useState('');
  const [passConfirm, setPassConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async () => {
    if (!email || !pass || !passConfirm) return;
    if (pass !== passConfirm) {
      setError('Şifreler eşleşmiyor.');
      return;
    }
    if (pass.length < 8) {
      setError('Şifre en az 8 karakter olmalıdır.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await register({ email, password: pass, full_name: fullName || undefined });
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail || 'Kayıt başarısız. Lütfen tekrar deneyin.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#040d1a] via-[#0a1628] to-[#0d1f35] font-['Outfit',sans-serif] relative overflow-hidden">
      {/* Animated Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 rounded-full bg-[#c9a227] opacity-15 animate-float"
            style={{
              left: `${(i * 37 + 13) % 100}%`,
              top: `${(i * 53 + 7) % 100}%`,
              animationDelay: `${(i * 0.4) % 5}s`,
              animationDuration: `${3 + (i % 4)}s`,
            }}
          />
        ))}
      </div>

      {/* Register Card */}
      <div className="w-[420px] p-10 bg-gradient-to-br from-[#0d1f3588] to-[#0a162888] border border-[#1e3a5f] rounded-[20px] backdrop-blur-[20px] relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="mb-3 flex justify-center">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <path d="M24 4L42 14V34L24 44L6 34V14L24 4Z" fill="url(#grad1r)" opacity="0.9" />
              <path d="M24 4L42 14V34L24 44L6 34V14L24 4Z" stroke="#c9a227" strokeWidth="1.5" fill="none" />
              <circle cx="24" cy="24" r="8" fill="#0a1628" stroke="#c9a227" strokeWidth="1.5" />
              <circle cx="24" cy="24" r="3" fill="#c9a227" />
              <defs>
                <linearGradient id="grad1r" x1="6" y1="4" x2="42" y2="44">
                  <stop offset="0%" stopColor="#0a1628" />
                  <stop offset="100%" stopColor="#132744" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 className="text-[26px] font-bold text-[#e2e8f0] m-0 tracking-tight">TradeRadar</h1>
          <p className="text-sm text-[#64748b] mt-1 tracking-widest uppercase">Yeni Hesap Oluştur</p>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 p-3 bg-[#ef444422] border border-[#ef4444] rounded-lg text-sm text-[#ef4444] flex items-start gap-2">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Full Name */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-[#94a3b8] mb-2 uppercase tracking-wider">
            Ad Soyad <span className="text-[#475569] normal-case tracking-normal">(opsiyonel)</span>
          </label>
          <input
            className="w-full px-4 py-3.5 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-[15px] outline-none transition-all focus:border-[#c9a22766]"
            placeholder="Yasin Özcan"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
          />
        </div>

        {/* Email */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-[#94a3b8] mb-2 uppercase tracking-wider">
            E-posta
          </label>
          <input
            type="email"
            className="w-full px-4 py-3.5 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-[15px] outline-none transition-all focus:border-[#c9a22766]"
            placeholder="kullanici@firma.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
          />
        </div>

        {/* Password */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-[#94a3b8] mb-2 uppercase tracking-wider">
            Şifre
          </label>
          <input
            type="password"
            className="w-full px-4 py-3.5 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-[15px] outline-none transition-all focus:border-[#c9a22766]"
            placeholder="En az 8 karakter"
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
          />
        </div>

        {/* Password Confirm */}
        <div className="mb-5">
          <label className="block text-xs font-medium text-[#94a3b8] mb-2 uppercase tracking-wider">
            Şifre Tekrar
          </label>
          <input
            type="password"
            className="w-full px-4 py-3.5 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-[15px] outline-none transition-all focus:border-[#c9a22766]"
            placeholder="••••••••"
            value={passConfirm}
            onChange={(e) => setPassConfirm(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRegister()}
          />
        </div>

        {/* Register Button */}
        <button
          onClick={handleRegister}
          disabled={loading || !email || !pass || !passConfirm}
          className="w-full px-4 py-3.5 bg-gradient-to-br from-[#c9a227] to-[#a07d18] border-none rounded-lg text-[#0a1628] text-base font-semibold cursor-pointer flex items-center justify-center min-h-[48px] mt-2 disabled:opacity-50 disabled:cursor-not-allowed hover:brightness-110 transition-all"
        >
          {loading ? (
            <span className="w-5 h-5 border-[2.5px] border-[#0a162844] border-t-[#0a1628] rounded-full animate-spin" />
          ) : (
            '🚀 Hesap Oluştur'
          )}
        </button>

        {/* Divider */}
        <div className="flex items-center gap-3 my-5">
          <div className="flex-1 h-px bg-[#1e3a5f]" />
          <span className="text-xs text-[#475569]">veya</span>
          <div className="flex-1 h-px bg-[#1e3a5f]" />
        </div>

        {/* Login Link */}
        <p className="text-center text-[13px] text-[#64748b]">
          Zaten hesabın var mı?{' '}
          <Link href="/tr/login" className="text-[#c9a227] font-semibold hover:text-[#e8c84a] transition-colors underline-offset-2">
            Giriş Yap
          </Link>
        </p>
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
