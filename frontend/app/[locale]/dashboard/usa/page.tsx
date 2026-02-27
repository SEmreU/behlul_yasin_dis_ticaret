'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';

const USA_SOURCES = [
    { id: 'thomasnet', name: 'Thomasnet', color: '#e11d48', desc: 'ABD/Kanada endüstriyel üretici rehberi' },
    { id: 'import_records', name: 'ImportGenius / Panjiva', color: '#0ea5e9', desc: 'ABD gümrük beyanı kayıtları' },
    { id: 'kompass_usa', name: 'Kompass USA', color: '#8b5cf6', desc: 'Kuzey Amerika firma rehberi' },
    { id: 'usitc', name: 'USITC Dataweb', color: '#f59e0b', desc: 'Resmi ABD ithalat istatistik' },
];

interface USAResult {
    source: string;
    title: string;
    company: string;
    location?: string;
    country: string;
    url: string;
    type?: string;
    note?: string;
}

export default function USAPage() {
    const [query, setQuery] = useState('');
    const [state, setState] = useState('');
    const [companyType, setCompanyType] = useState('');
    const [hsCode, setHsCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<Record<string, USAResult[]> | null>(null);
    const [totalResults, setTotalResults] = useState(0);
    const [error, setError] = useState('');
    const [expandedSource, setExpandedSource] = useState<string | null>(null);

    const handleSearch = async () => {
        if (!query.trim()) {
            setError('Ürün / sektör adı girin');
            return;
        }
        setLoading(true);
        setError('');
        setResults(null);

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${API_URL}/api/v1/marketplace/search-usa`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({
                    query,
                    state: state || undefined,
                    company_type: companyType || undefined,
                    hs_code: hsCode || undefined,
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

    const allItems = results
        ? Object.values(results).flat()
        : [];

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🇺🇸 ABD Pazarı Detaylı Arama</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Thomasnet, ImportGenius, Panjiva ve Kompass ile ABD ithalatçıları bulun
                    </p>
                </div>

                {/* Info */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong className="text-[#00e5a0]">Veri Kaynakları:</strong>{' '}
                    Thomasnet (endüstriyel üretici), ImportGenius/Panjiva (gümrük beyanı), Kompass USA (firma rehberi), USITC (resmi istatistik).
                    ScraperAPI key eklenirse Thomasnet&apos;ten gerçek firma listesi çekilir.
                </div>

                {/* Source Badges */}
                <div className="flex flex-wrap gap-2 mb-5">
                    {USA_SOURCES.map(s => (
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
                            Ürün / Sektör <span className="text-[#00e5a0]">*</span>
                        </label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: auto parts, hydraulic pump, steel..."
                            value={query}
                            onChange={e => setQuery(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSearch()}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Eyalet (Opsiyonel)</label>
                        <select
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            value={state}
                            onChange={e => setState(e.target.value)}
                        >
                            <option value="">Tüm ABD</option>
                            <option value="California">California</option>
                            <option value="Texas">Texas</option>
                            <option value="Florida">Florida</option>
                            <option value="New York">New York</option>
                            <option value="Michigan">Michigan</option>
                            <option value="Ohio">Ohio</option>
                            <option value="Illinois">Illinois</option>
                            <option value="Pennsylvania">Pennsylvania</option>
                            <option value="Georgia">Georgia</option>
                            <option value="North Carolina">North Carolina</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Firma Tipi</label>
                        <select
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            value={companyType}
                            onChange={e => setCompanyType(e.target.value)}
                        >
                            <option value="">Hepsi</option>
                            <option value="importer">İthalatçı</option>
                            <option value="distributor">Distribütör</option>
                            <option value="oem">OEM Üretici</option>
                            <option value="retailer">Perakendeci</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">HS / GTİP Kodu (Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: 8409"
                            value={hsCode}
                            onChange={e => setHsCode(e.target.value)}
                        />
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
                    {loading ? '⏳ Aranıyor...' : '🔍 ABD Müşteri Ara'}
                </button>

                {/* Results */}
                {results && (
                    <div className="mt-8">
                        <h3 className="text-xl font-bold text-[#e2e8f0] mb-4">
                            📊 {totalResults} kayıt bulundu
                        </h3>

                        <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl overflow-hidden">
                            <table className="w-full border-collapse">
                                <thead>
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Kaynak</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Firma / Başlık</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Konum</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Tip</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase border-b border-[#1e3a5f44] bg-[#0a162888]">Link</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {allItems.map((item, i) => (
                                        <tr key={i} className="border-b border-[#1e3a5f22] last:border-0 hover:bg-[#ffffff04] transition-colors">
                                            <td className="px-4 py-3 text-sm">
                                                <span className="px-2 py-1 bg-[#e11d4822] text-[#e11d48] rounded text-xs font-medium">{item.source}</span>
                                            </td>
                                            <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                <strong>{item.title}</strong>
                                                {item.note && <div className="text-xs text-[#64748b] mt-0.5">{item.note}</div>}
                                            </td>
                                            <td className="px-4 py-3 text-sm text-[#94a3b8]">{item.location || item.country || 'USA'}</td>
                                            <td className="px-4 py-3 text-xs text-[#64748b]">{item.type || '-'}</td>
                                            <td className="px-4 py-3 text-sm">
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

                        {/* Source breakdown */}
                        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
                            {Object.entries(results).map(([src, items]) => {
                                const info = USA_SOURCES.find(s => s.id === src);
                                return (
                                    <button key={src}
                                        onClick={() => setExpandedSource(expandedSource === src ? null : src)}
                                        className="bg-[#0d1f35] border border-[#1e3a5f44] rounded-xl p-3 text-left hover:border-[#1e3a5f] transition-colors"
                                    >
                                        <div className="text-xs text-[#64748b]">{info?.name || src}</div>
                                        <div className="text-lg font-bold text-[#00e5a0]">{items.length}</div>
                                        <div className="text-xs text-[#94a3b8]">sonuç</div>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
