'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';

interface MapResult {
    name: string;
    address: string;
    country: string;
    city: string;
    rating?: number;
    website?: string;
    phone?: string;
    lat?: number;
    lng?: number;
    source: string;
}

interface MapsResponse {
    success: boolean;
    total_results: number;
    results: MapResult[];
    note?: string;
}

export default function MapsPage() {
    const [keyword, setKeyword] = useState('');
    const [country, setCountry] = useState('');
    const [city, setCity] = useState('');
    const [language, setLanguage] = useState('en');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<MapResult[] | null>(null);
    const [total, setTotal] = useState(0);
    const [error, setError] = useState('');
    const [note, setNote] = useState('');

    // Selected place for map embed
    const [selectedPlace, setSelectedPlace] = useState('');

    const handleSearch = async () => {
        if (!keyword.trim()) { setError('Anahtar kelime girin'); return; }
        setLoading(true);
        setError('');
        setResults(null);
        setNote('');

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${API_URL}/api/v1/maps/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({
                    keywords: keyword,
                    country: country || undefined,
                    city: city || undefined,
                    language,
                }),
            });

            const data: MapsResponse = await res.json();
            if (res.ok) {
                setResults(data.results || []);
                setTotal(data.total_results || 0);
                if (data.note) setNote(data.note);
                // Center map on first result
                if (data.results?.[0]) {
                    const first = data.results[0];
                    setSelectedPlace(first.name + ' ' + (first.address || first.city || first.country));
                } else if (country || city) {
                    setSelectedPlace([city, country].filter(Boolean).join(', '));
                }
            } else {
                setError((data as { detail?: string }).detail || 'Arama başarısız');
            }
        } catch {
            setError('Sunucuya bağlanılamadı');
        } finally {
            setLoading(false);
        }
    };

    const mapsEmbedSrc = selectedPlace
        ? `https://maps.google.com/maps?q=${encodeURIComponent(selectedPlace)}&t=m&z=9&output=embed&iwloc=near`
        : `https://maps.google.com/maps?q=Turkey&t=m&z=5&output=embed&iwloc=near`;

    const handleExport = async () => {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const token = localStorage.getItem('access_token');
        const url = `${API_URL}/api/v1/maps/export?keywords=${encodeURIComponent(keyword)}&country=${encodeURIComponent(country)}&city=${encodeURIComponent(city)}`;
        const a = document.createElement('a');
        a.href = url;
        a.target = '_blank';
        a.click();
    };

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Header */}
                <div className="mb-7 flex justify-between items-start">
                    <div>
                        <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🗺️ Harita ile Firma Arama</h2>
                        <p className="text-[15px] text-[#64748b] mt-2">
                            Google Maps entegrasyonu ile ülke/şehir bazlı firma ve ithalatçı bulun
                        </p>
                    </div>
                    {results && results.length > 0 && (
                        <button
                            onClick={handleExport}
                            className="px-4 py-2 bg-[#10b981] text-white rounded-lg text-sm font-medium hover:bg-[#059669] transition-colors"
                        >
                            📊 Excel İndir
                        </button>
                    )}
                </div>

                {/* Info */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong className="text-[#00e5a0]">Google Maps API key ekleyin</strong> (Ayarlar → Harita & Konum) →
                    gerçek firma verileri + konum haritası. Key olmadan mock verilerle çalışır.
                </div>

                {/* Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
                    <div className="lg:col-span-2">
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            Anahtar Kelime <span className="text-[#00e5a0]">*</span>
                        </label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: auto parts importer, hydraulic machinery..."
                            value={keyword}
                            onChange={e => setKeyword(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSearch()}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ülke</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: Germany, Russia..."
                            value={country}
                            onChange={e => setCountry(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Şehir</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: Berlin, Moscow..."
                            value={city}
                            onChange={e => setCity(e.target.value)}
                        />
                    </div>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                        ⚠️ {error}
                    </div>
                )}

                {note && (
                    <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-300 text-sm">
                        ℹ️ {note}
                    </div>
                )}

                <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer disabled:opacity-50 transition-opacity mb-6"
                >
                    {loading ? '⏳ Aranıyor...' : '🗺️ Haritada Ara'}
                </button>

                {/* Map + Results side by side */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Map embed */}
                    <div>
                        <div className="text-sm text-[#64748b] mb-2">📍 Harita Görünümü</div>
                        <div className="rounded-2xl overflow-hidden border border-[#1e3a5f44]" style={{ height: '420px' }}>
                            <iframe
                                width="100%"
                                height="100%"
                                frameBorder="0"
                                scrolling="no"
                                marginHeight={0}
                                marginWidth={0}
                                src={mapsEmbedSrc}
                                title="Google Maps"
                            />
                        </div>
                        <div className="text-xs text-[#64748b] mt-2">
                            Not: Konum haritası için{' '}
                            <a href="https://console.cloud.google.com" target="_blank" rel="noreferrer"
                                className="text-[#00e5a0] hover:underline">
                                Google Maps API key
                            </a>{' '}
                            gereklidir.
                        </div>
                    </div>

                    {/* Results table */}
                    <div>
                        {results === null && !loading && (
                            <div className="h-[420px] flex items-center justify-center text-[#64748b] text-sm border border-[#1e3a5f22] rounded-2xl">
                                Arama yapın → sonuçlar burada görünür
                            </div>
                        )}

                        {results !== null && (
                            <>
                                <div className="text-sm text-[#64748b] mb-2">
                                    📊 {total} firma bulundu
                                </div>
                                <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl overflow-hidden"
                                    style={{ maxHeight: '420px', overflowY: 'auto' }}>
                                    {results.length === 0 ? (
                                        <div className="p-8 text-center text-[#64748b]">Sonuç bulunamadı</div>
                                    ) : (
                                        <table className="w-full border-collapse text-sm">
                                            <thead className="sticky top-0">
                                                <tr>
                                                    <th className="px-3 py-2 text-left text-xs font-semibold text-[#64748b] uppercase bg-[#0a162888] border-b border-[#1e3a5f44]">Firma</th>
                                                    <th className="px-3 py-2 text-left text-xs font-semibold text-[#64748b] uppercase bg-[#0a162888] border-b border-[#1e3a5f44]">Konum</th>
                                                    <th className="px-3 py-2 text-left text-xs font-semibold text-[#64748b] uppercase bg-[#0a162888] border-b border-[#1e3a5f44]">İletişim</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {results.map((r, i) => (
                                                    <tr key={i}
                                                        onClick={() => setSelectedPlace(r.name + ' ' + (r.address || r.city))}
                                                        className="border-b border-[#1e3a5f22] last:border-0 hover:bg-[#00e5a008] cursor-pointer transition-colors">
                                                        <td className="px-3 py-2.5 text-[#cbd5e1]">
                                                            <strong className="text-[13px]">{r.name}</strong>
                                                        </td>
                                                        <td className="px-3 py-2.5 text-[#94a3b8] text-xs">
                                                            {r.city || r.address || r.country}
                                                        </td>
                                                        <td className="px-3 py-2.5 text-xs">
                                                            {r.website && (
                                                                <a href={r.website.startsWith('http') ? r.website : 'https://' + r.website}
                                                                    target="_blank" rel="noopener noreferrer"
                                                                    className="text-[#00e5a0] hover:underline block">
                                                                    🔗 Site
                                                                </a>
                                                            )}
                                                            {r.phone && <div className="text-[#64748b]">📞 {r.phone}</div>}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
