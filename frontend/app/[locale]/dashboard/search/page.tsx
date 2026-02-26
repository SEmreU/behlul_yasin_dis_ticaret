'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import api from '@/lib/api';

const COUNTRIES = [
    'Almanya', 'İngiltere', 'Fransa', 'İtalya', 'İspanya', 'Hollanda', 'Belçika',
    'Avusturya', 'İsviçre', 'Polonya', 'Çekya', 'Romanya', 'Bulgaristan', 'Yunanistan',
    'ABD', 'Kanada', 'Brezilya', 'Meksika', 'Çin', 'Hindistan', 'Japonya', 'Güney Kore',
    'BAE', 'Suudi Arabistan', 'Mısır', 'Nijerya', 'Rusya', 'Ukrayna', 'Polonya',
];

const LANGUAGE_MAP: Record<string, string> = {
    'İngilizce': 'en', 'Almanca': 'de', 'Fransızca': 'fr', 'İspanyolca': 'es',
    'İtalyanca': 'it', 'Portekizce': 'pt', 'Rusça': 'ru', 'Arapça': 'ar',
    'Çince (Mandarin)': 'zh', 'Japonca': 'ja', 'Korece': 'ko', 'Türkçe': 'tr',
};

const SEARCH_ENGINES = ['Google', 'Yandex', 'Bing', 'Baidu', 'DuckDuckGo', 'Yahoo'];
const DB_SOURCES = [
    'TradeAtlas', 'ImportGenius', 'Trademo Intel', 'Panjiva',
    'Global Buyers Online', 'Europages', 'TradeKey', 'TradeMap', 'UN Comtrade'
];

interface SearchResult {
    id?: number | string;
    company_name?: string;
    title?: string;
    name?: string;
    country?: string;
    email?: string;
    phone?: string;
    website?: string;
    url?: string;
    gtip_code?: string;
    oem_code?: string;
    category?: string;
    source?: string;
    descriptions?: Record<string, string>;
    [key: string]: unknown;
}

export default function SearchPage() {
    const [searchType, setSearchType] = useState<'text' | 'image'>('text');
    const [formData, setFormData] = useState({
        product: '',
        gtip: '',
        oemNo: '',
        country: '',
        language: '',
        linkedSectors: '',
        competitors: '',
    });
    const [selectedEngines, setSelectedEngines] = useState<string[]>(SEARCH_ENGINES);
    const [selectedDBs, setSelectedDBs] = useState<string[]>(DB_SOURCES);

    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<SearchResult[] | null>(null);
    const [resultsCount, setResultsCount] = useState(0);
    const [error, setError] = useState('');

    const toggleItem = (arr: string[], setArr: (v: string[]) => void, item: string) => {
        setArr(arr.includes(item) ? arr.filter(i => i !== item) : [...arr, item]);
    };

    const buildQuery = () => {
        const parts = [];
        if (formData.product) parts.push(formData.product);
        if (formData.gtip) parts.push(`GTİP:${formData.gtip}`);
        if (formData.oemNo) parts.push(`OEM:${formData.oemNo}`);
        if (formData.competitors) parts.push(formData.competitors);
        if (formData.linkedSectors) parts.push(formData.linkedSectors);
        if (formData.country) parts.push(formData.country);
        return parts.join(' ');
    };

    const getSearchLang = () => {
        if (!formData.language || formData.language === 'auto') return 'tr';
        return LANGUAGE_MAP[formData.language] || 'en';
    };

    const getSearchType = () => {
        if (formData.gtip && !formData.product) return 'gtip';
        if (formData.oemNo && !formData.product) return 'oem';
        return 'text';
    };

    const handleSearch = async () => {
        const query = buildQuery();
        if (!query.trim()) {
            setError('Lütfen en az bir arama kriteri girin');
            return;
        }

        setLoading(true);
        setError('');
        setResults(null);

        try {
            const res = await api.post('/search/product', {
                query: query.trim(),
                language: getSearchLang(),
                search_type: getSearchType(),
                max_results: 50,
            });
            setResults(res.data.results || []);
            setResultsCount(res.data.results_count || 0);
        } catch (e: unknown) {
            const err = e as { response?: { data?: { detail?: string } } };
            setError(err?.response?.data?.detail || 'Arama sırasında hata oluştu');
        } finally {
            setLoading(false);
        }
    };

    const handleExcel = async () => {
        const query = buildQuery();
        if (!results || !query) { alert('Önce arama yapın'); return; }
        try {
            const res = await api.get(`/search/product/export?query=${encodeURIComponent(query)}`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const a = document.createElement('a');
            a.href = url;
            a.download = `arama_sonuclari_${query}.xlsx`;
            a.click();
        } catch {
            alert('Excel indirme özelliği yakında eklenecek');
        }
    };

    const getDisplayName = (r: SearchResult) =>
        r.company_name || r.title || r.name || '—';
    const getDisplayCountry = (r: SearchResult) => r.country || '—';
    const getDisplayContact = (r: SearchResult) => r.email || r.phone || '—';
    const getDisplayLink = (r: SearchResult) => r.website || r.url || null;
    const getDisplaySource = (r: SearchResult) => r.source || r.category || '—';

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🔍 Potansiyel Müşteri Arama</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        AI destekli arama motorları ve dış ticaret veritabanları ile potansiyel alıcılarınızı bulun
                    </p>
                </div>

                {/* Search Tabs */}
                <div className="flex gap-2 mb-6">
                    <button
                        onClick={() => setSearchType('text')}
                        className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${searchType === 'text'
                            ? 'bg-[#00e5a012] border border-[#00e5a044] text-[#00e5a0]'
                            : 'bg-transparent border border-[#1e3a5f] text-[#64748b]'
                            }`}
                    >
                        📝 Metin ile Ara
                    </button>
                    <button
                        onClick={() => setSearchType('image')}
                        className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${searchType === 'image'
                            ? 'bg-[#00e5a012] border border-[#00e5a044] text-[#00e5a0]'
                            : 'bg-transparent border border-[#1e3a5f] text-[#64748b]'
                            }`}
                    >
                        🖼 Ürün Resmi ile Ara
                    </button>
                </div>

                {/* Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    {searchType === 'text' ? (
                        <>
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ürün / Parça Adı</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: piston, brake pad, gear box..."
                                    value={formData.product}
                                    onChange={e => setFormData({ ...formData, product: e.target.value })}
                                    onKeyDown={e => e.key === 'Enter' && handleSearch()}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">IATE + Cambridge Sözlük doğrulaması yapılır</span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">GTİP Kodu</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: 8409.91"
                                    value={formData.gtip}
                                    onChange={e => setFormData({ ...formData, gtip: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">Bağlı / Tamamlayıcı GTİP&apos;ler otomatik sorgulanır</span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">OEM No (Opsiyonel)</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: 12345-ABC-67890"
                                    value={formData.oemNo}
                                    onChange={e => setFormData({ ...formData, oemNo: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">OEM numarası ile doğrudan eşleşme</span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Hedef Ülke</label>
                                <select
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    value={formData.country}
                                    onChange={e => setFormData({ ...formData, country: e.target.value })}
                                >
                                    <option value="">Ülke seçin...</option>
                                    <option value="all">🌍 Tüm Ülkeler</option>
                                    {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
                                </select>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Arama Dili</label>
                                <select
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    value={formData.language}
                                    onChange={e => setFormData({ ...formData, language: e.target.value })}
                                >
                                    <option value="">Dil seçin...</option>
                                    <option value="auto">🤖 Otomatik (Ülkeye göre)</option>
                                    {Object.keys(LANGUAGE_MAP).map(l => <option key={l} value={l}>{l}</option>)}
                                </select>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Bağlı Sektörler</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: hırdavat, otomotiv yedek parça..."
                                    value={formData.linkedSectors}
                                    onChange={e => setFormData({ ...formData, linkedSectors: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">İkincil ithalatçıları yakalamak için tamamlayıcı sektörler</span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Rakip Firmalar / Markalar</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: Mahle, Federal Mogul, NPR..."
                                    value={formData.competitors}
                                    onChange={e => setFormData({ ...formData, competitors: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">Rakip markaları aratan müşteriler de taranır</span>
                            </div>
                        </>
                    ) : (
                        <div className="col-span-2">
                            <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ürün Görseli Yükle</label>
                            <div className="border-2 border-dashed border-[#1e3a5f] rounded-2xl p-10 text-center cursor-pointer hover:border-[#00e5a044] transition-colors">
                                <div className="text-5xl mb-3">📸</div>
                                <p className="text-[#94a3b8] m-0">Ürün görselini sürükleyin veya tıklayarak seçin</p>
                                <p className="text-[#64748b] text-[13px] mt-2">Görüntü işleme ile eşleşen web siteleri taranacaktır</p>
                                <button className="mt-4 px-6 py-2.5 bg-[#1e3a5f] border-none rounded-lg text-[#e2e8f0] text-sm cursor-pointer hover:bg-[#2a4a6f] transition-colors">
                                    Dosya Seç
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Search Engines */}
                <div className="mt-4 p-5 bg-[#0a162888] border border-[#1e3a5f33] rounded-xl mb-4">
                    <h4 className="text-sm font-semibold text-[#94a3b8] m-0 mb-3">Taranacak Arama Motorları</h4>
                    <div className="flex flex-wrap gap-2.5">
                        {SEARCH_ENGINES.map(e => (
                            <label key={e} className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0d1f35] rounded-lg text-[13px] text-[#cbd5e1] cursor-pointer hover:bg-[#1e3a5f] transition-colors">
                                <input
                                    type="checkbox"
                                    checked={selectedEngines.includes(e)}
                                    onChange={() => toggleItem(selectedEngines, setSelectedEngines, e)}
                                    className="accent-[#00e5a0]"
                                />
                                {e}
                            </label>
                        ))}
                    </div>
                </div>

                {/* DB Sources */}
                <div className="p-5 bg-[#0a162888] border border-[#1e3a5f33] rounded-xl">
                    <h4 className="text-sm font-semibold text-[#94a3b8] m-0 mb-3">Dış Ticaret Veritabanları</h4>
                    <div className="flex flex-wrap gap-2.5">
                        {DB_SOURCES.map(s => (
                            <label key={s} className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0d1f35] rounded-lg text-[13px] text-[#cbd5e1] cursor-pointer hover:bg-[#1e3a5f] transition-colors">
                                <input
                                    type="checkbox"
                                    checked={selectedDBs.includes(s)}
                                    onChange={() => toggleItem(selectedDBs, setSelectedDBs, s)}
                                    className="accent-[#0ea5e9]"
                                />
                                {s}
                            </label>
                        ))}
                    </div>
                </div>

                {error && (
                    <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                        ⚠️ {error}
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 mt-6">
                    <button
                        onClick={handleSearch}
                        disabled={loading}
                        className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer hover:brightness-110 disabled:opacity-50 transition-all"
                    >
                        {loading ? '⏳ Aranıyor...' : '🚀 Aramayı Başlat'}
                    </button>
                    {results && results.length > 0 && (
                        <button
                            onClick={handleExcel}
                            className="px-8 py-3.5 bg-transparent border border-[#1e3a5f] rounded-xl text-[#94a3b8] text-[15px] font-medium cursor-pointer hover:bg-[#1e3a5f22] transition-all"
                        >
                            📊 Excel Olarak İndir
                        </button>
                    )}
                </div>

                {/* Results Table */}
                {results && (
                    <div className="mt-8">
                        <h3 className="text-xl font-bold text-[#e2e8f0] mb-4">
                            📊 {resultsCount} Sonuç Bulundu
                        </h3>

                        {results.length === 0 ? (
                            <div className="bg-[#0d1f35] border border-[#1e3a5f44] rounded-2xl p-8 text-center text-[#64748b]">
                                <div className="text-4xl mb-3">🔍</div>
                                <p>Sonuç bulunamadı. Farklı anahtar kelimeler deneyin veya ScraperAPI key ekleyin.</p>
                            </div>
                        ) : (
                            <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl overflow-hidden">
                                <table className="w-full border-collapse">
                                    <thead>
                                        <tr className="bg-[#0a162888]">
                                            <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44]">Şirket / Ürün</th>
                                            <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44]">Ülke</th>
                                            <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44]">Kaynak</th>
                                            <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44]">İletişim</th>
                                            <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44]">Link</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {results.map((r, i) => (
                                            <tr key={i} className="border-b border-[#1e3a5f22] last:border-0 hover:bg-[#0d1f3522] transition-colors">
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                    <strong>{getDisplayName(r)}</strong>
                                                    {r.gtip_code && <span className="ml-2 px-1.5 py-0.5 bg-[#00e5a011] text-[#00e5a0] rounded text-xs">GTİP: {r.gtip_code}</span>}
                                                    {r.oem_code && <span className="ml-2 px-1.5 py-0.5 bg-[#0ea5e911] text-[#0ea5e9] rounded text-xs">OEM: {r.oem_code}</span>}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">{getDisplayCountry(r)}</td>
                                                <td className="px-4 py-3 text-sm">
                                                    <span className="px-2 py-0.5 bg-[#8b5cf611] text-[#8b5cf6] rounded text-xs">{getDisplaySource(r)}</span>
                                                </td>
                                                <td className="px-4 py-3 text-sm text-[#94a3b8] font-mono text-xs">{getDisplayContact(r)}</td>
                                                <td className="px-4 py-3 text-sm">
                                                    {getDisplayLink(r) ? (
                                                        <a href={getDisplayLink(r)!} target="_blank" rel="noopener noreferrer"
                                                            className="text-[#00e5a0] hover:underline text-xs">
                                                            🔗 Görüntüle
                                                        </a>
                                                    ) : <span className="text-[#475569]">—</span>}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
