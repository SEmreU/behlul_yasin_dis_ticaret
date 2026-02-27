'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';

const CHINA_SOURCES = [
    { id: 'alibaba', name: 'Alibaba.com', color: '#ff6600' },
    { id: 'made_in_china', name: 'Made-in-China', color: '#e11d48' },
    { id: 'dhgate', name: 'DHgate', color: '#06b6d4' },
    { id: '1688', name: '1688.com', color: '#f59e0b' },
    { id: 'global_sources', name: 'Global Sources', color: '#10b981' },
];

interface ChinaResult {
    source: string;
    title: string;
    supplier?: string;
    company?: string;
    price?: string;
    country: string;
    url: string;
    type?: string;
    note?: string;
}

export default function ChinaPage() {
    const [query, setQuery] = useState('');
    const [queryChinese, setQueryChinese] = useState('');
    const [minOrder, setMinOrder] = useState('');
    const [certificate, setCertificate] = useState('Hepsi');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<Record<string, ChinaResult[]> | null>(null);
    const [totalResults, setTotalResults] = useState(0);
    const [error, setError] = useState('');

    const handleSearch = async () => {
        if (!query.trim()) {
            setError('Ürün adı girin');
            return;
        }
        setLoading(true);
        setError('');
        setResults(null);

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${API_URL}/api/v1/marketplace/search-china`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({
                    query,
                    query_chinese: queryChinese || undefined,
                    min_order: minOrder || undefined,
                    certificate: certificate !== 'Hepsi' ? certificate : undefined,
                    max_results: 20,
                }),
            });

            if (res.ok) {
                const data = await res.json();
                setResults(data.results || {});
                setTotalResults(data.total_results || 0);
            } else {
                const err = await res.json().catch(() => ({}));
                setError(err.detail || 'Arama başarısız oldu');
            }
        } catch {
            setError('Sunucuya bağlanılamadı');
        } finally {
            setLoading(false);
        }
    };

    const allItems: ChinaResult[] = results ? Object.values(results).flat() : [];

    const sourceColor = (src: string) =>
        CHINA_SOURCES.find(s => s.id === src)?.color || '#64748b';

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🇨🇳 Çin Pazarı Özel Arama</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Alibaba, Made-in-China, DHgate, 1688 ve Global Sources ile Çinli tedarikçi bulun
                    </p>
                </div>

                {/* Info */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong className="text-[#00e5a0]">ScraperAPI key ekleyin</strong> → Alibaba ve Made-in-China&apos;dan gerçek ürün, fiyat ve tedarikçi bilgisi çekilir.
                    Key olmadan doğrudan arama linkleri döner.
                </div>

                {/* Source Badges */}
                <div className="flex flex-wrap gap-2 mb-5">
                    {CHINA_SOURCES.map(s => (
                        <span key={s.id} className="px-3 py-1 rounded-full text-xs font-medium border"
                            style={{ color: s.color, borderColor: s.color + '44', background: s.color + '11' }}>
                            {s.name}
                        </span>
                    ))}
                </div>

                {/* Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            Ürün Adı (İngilizce) <span className="text-[#00e5a0]">*</span>
                        </label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: hydraulic cylinder, auto spare parts..."
                            value={query}
                            onChange={e => setQuery(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSearch()}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ürün Adı (Çince — Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="液压缸 (1688 araması için)"
                            value={queryChinese}
                            onChange={e => setQueryChinese(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Minimum Sipariş Miktarı (Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: 100 adet"
                            value={minOrder}
                            onChange={e => setMinOrder(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Sertifika Gereksinimi</label>
                        <select
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            value={certificate}
                            onChange={e => setCertificate(e.target.value)}
                        >
                            <option>Hepsi</option>
                            <option>ISO 9001</option>
                            <option>CE</option>
                            <option>SGS Denetimli</option>
                        </select>
                    </div>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                        ⚠️ {error}
                    </div>
                )}

                <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer disabled:opacity-50 transition-opacity"
                >
                    {loading ? '⏳ Aranıyor...' : '🔍 Çin Tedarikçi Ara'}
                </button>

                {/* Results */}
                {results && (
                    <div className="mt-8">
                        <h3 className="text-xl font-bold text-[#e2e8f0] mb-4">
                            📊 {totalResults} kayıt bulundu
                        </h3>

                        {/* Source stat cards */}
                        <div className="flex flex-wrap gap-3 mb-5">
                            {Object.entries(results).map(([src, items]) => {
                                const info = CHINA_SOURCES.find(s => s.id === src);
                                return (
                                    <div key={src}
                                        className="bg-[#0d1f35] border border-[#1e3a5f44] rounded-xl px-4 py-2 min-w-[90px] text-center"
                                        style={{ borderColor: (info?.color || '#1e3a5f') + '44' }}
                                    >
                                        <div className="text-xl font-bold" style={{ color: info?.color || '#00e5a0' }}>{items.length}</div>
                                        <div className="text-xs text-[#64748b]">{info?.name || src}</div>
                                    </div>
                                );
                            })}
                        </div>

                        <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl overflow-hidden">
                            <table className="w-full border-collapse">
                                <thead>
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Platform</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Ürün / Başlık</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Tedarikçi</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Fiyat</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Link</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {allItems.map((item, i) => (
                                        <tr key={i} className="border-b border-[#1e3a5f22] last:border-0 hover:bg-[#ffffff04] transition-colors">
                                            <td className="px-4 py-3">
                                                <span className="px-2 py-1 rounded text-xs font-medium"
                                                    style={{ color: sourceColor(item.source.replace('.', '_').replace('-', '_')), background: sourceColor(item.source.replace('.', '_').replace('-', '_')) + '22' }}>
                                                    {item.source}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                <strong>{item.title}</strong>
                                                {item.note && <div className="text-xs text-[#64748b] mt-0.5">{item.note}</div>}
                                            </td>
                                            <td className="px-4 py-3 text-sm text-[#94a3b8]">{item.supplier || item.company || '—'}</td>
                                            <td className="px-4 py-3 text-sm text-[#00e5a0] font-medium">{item.price || '—'}</td>
                                            <td className="px-4 py-3">
                                                <a href={item.url} target="_blank" rel="noopener noreferrer"
                                                    className="text-[#00e5a0] hover:underline text-xs">
                                                    🔗 Aç
                                                </a>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
