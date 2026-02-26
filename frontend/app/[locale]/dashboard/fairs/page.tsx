'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import api from '@/lib/api';

interface Fair {
    id: number;
    name: string;
    location: string;
    country: string;
    date: string;
    end_date: string;
    sector: string[];
    website: string;
    exhibitors_count: number;
    visitors_count: number;
    description: string;
    match_score?: number;
    match_reasons?: string[];
    relevance?: string;
}

interface FairsResult {
    matched_fairs: Fair[];
    total_matched: number;
    ai_summary: string | null;
    keywords_used: string[];
}

export default function FairsPage() {
    const [keywords, setKeywords] = useState('');
    const [gtipCode, setGtipCode] = useState('');
    const [targetCountry, setTargetCountry] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<FairsResult | null>(null);
    const [error, setError] = useState('');

    const handleAnalyze = async () => {
        const kwList = keywords.split(',').map(k => k.trim()).filter(Boolean);
        if (kwList.length === 0) {
            setError('Lütfen en az bir ürün/sektör anahtar kelimesi girin');
            return;
        }

        setLoading(true);
        setError('');
        setResults(null);

        try {
            const payload: Record<string, unknown> = {
                product_keywords: kwList,
            };
            if (gtipCode.trim()) payload.gtip_codes = [gtipCode.trim()];
            if (targetCountry.trim()) payload.target_countries = [targetCountry.trim()];

            const res = await api.post('/fairs/match', payload);
            setResults(res.data);
        } catch (e: unknown) {
            const err = e as { response?: { data?: { detail?: string } } };
            setError(err?.response?.data?.detail || 'Bağlantı hatası oluştu');
        } finally {
            setLoading(false);
        }
    };

    const relevanceColor = (r?: string) => {
        if (r === 'Yüksek') return 'text-[#00e5a0] bg-[#00e5a011] border-[#00e5a033]';
        if (r === 'Orta') return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30';
        return 'text-[#64748b] bg-white/5 border-white/10';
    };

    return (
        <DashboardLayout>
            <div className="p-8">
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🎪 Fuar Analizi</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Ürün ve GTİP kodunuza göre en uygun uluslararası fuarları bulun — Groq AI ile açıklama
                    </p>
                </div>

                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong>Örnek Senaryo:</strong> Konya&apos;da piston üreten bir firma olarak Automechanika fuarlarına (Almanya, Dubai, Brezilya, Çin, ABD)
                    katılmak maliyetli. Bu modül 15 global fuarı tarayarak sizinle eşleşenleri puanlar ve
                    {' '}<span className="text-[#00e5a0]">Groq AI ile neden katılmanız gerektiğini açıklar.</span>
                </div>

                {/* Search Form */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
                    <div className="md:col-span-3">
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            Ürün / Sektör Anahtar Kelimeleri <span className="text-[#00e5a0]">*</span>
                        </label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: automotive, spare parts, piston (virgülle ayırın)"
                            value={keywords}
                            onChange={e => setKeywords(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">GTİP Kodu (Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: 8708"
                            value={gtipCode}
                            onChange={e => setGtipCode(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Hedef Ülke (Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: Germany, China"
                            value={targetCountry}
                            onChange={e => setTargetCountry(e.target.value)}
                        />
                    </div>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                        ⚠️ {error}
                    </div>
                )}

                <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer disabled:opacity-50 transition-opacity"
                >
                    {loading ? '⏳ Analiz ediliyor...' : '🔎 Fuarları Eşleştir'}
                </button>

                {/* AI Summary */}
                {results?.ai_summary && (
                    <div className="mt-6 p-4 bg-gradient-to-r from-[#8b5cf611] to-[#00e5a011] border border-[#8b5cf633] rounded-xl">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-purple-400 text-sm font-medium">🤖 Groq AI Özeti</span>
                        </div>
                        <p className="text-[#cbd5e1] text-sm leading-relaxed">{results.ai_summary}</p>
                    </div>
                )}

                {/* Results */}
                {results && (
                    <div className="mt-6">
                        <h3 className="text-xl font-bold text-[#e2e8f0] mb-4">
                            📊 {results.total_matched} Fuar Eşleşti
                        </h3>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            {results.matched_fairs.map((fair) => (
                                <div key={fair.id}
                                    className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl p-5 hover:border-[#1e3a5f] transition-colors">
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="flex-1">
                                            <h4 className="text-[#e2e8f0] font-semibold text-base">{fair.name}</h4>
                                            <p className="text-[#64748b] text-xs mt-0.5">📍 {fair.location}</p>
                                        </div>
                                        {fair.match_score !== undefined && (
                                            <div className="text-right ml-3">
                                                <div className="text-xl font-bold text-[#00e5a0]">{fair.match_score}</div>
                                                <span className={`text-xs px-2 py-0.5 rounded border ${relevanceColor(fair.relevance)}`}>
                                                    {fair.relevance}
                                                </span>
                                            </div>
                                        )}
                                    </div>

                                    <p className="text-[#94a3b8] text-sm mb-3 leading-relaxed">{fair.description}</p>

                                    <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
                                        <div>
                                            <span className="text-[#64748b]">📅 Tarih</span>
                                            <p className="text-[#cbd5e1] mt-0.5">{fair.date} → {fair.end_date}</p>
                                        </div>
                                        <div>
                                            <span className="text-[#64748b]">👥 Ziyaretçi</span>
                                            <p className="text-[#cbd5e1] mt-0.5">{fair.visitors_count.toLocaleString()}</p>
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap gap-1 mb-3">
                                        {fair.sector.slice(0, 3).map(s => (
                                            <span key={s} className="px-2 py-0.5 bg-[#1e3a5f] text-[#94a3b8] rounded text-xs">{s}</span>
                                        ))}
                                    </div>

                                    {fair.match_reasons && fair.match_reasons.length > 0 && (
                                        <div className="text-xs text-[#00e5a0] mb-3">
                                            ✓ {fair.match_reasons.join(' · ')}
                                        </div>
                                    )}

                                    <a href={fair.website} target="_blank" rel="noopener noreferrer"
                                        className="text-xs text-[#0ea5e9] hover:underline">
                                        🔗 Resmi Web Sitesi
                                    </a>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
