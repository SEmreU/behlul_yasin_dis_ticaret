'use client';

import { useState, useMemo } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import api from '@/lib/api';

const COUNTRIES = [
    'Almanya', 'İngiltere', 'Fransa', 'İtalya', 'İspanya', 'Hollanda', 'Belçika',
    'Avusturya', 'İsviçre', 'Polonya', 'Çekya', 'Romanya', 'Bulgaristan', 'Yunanistan',
    'ABD', 'Kanada', 'Brezilya', 'Meksika', 'Çin', 'Hindistan', 'Japonya', 'Güney Kore',
    'BAE', 'Suudi Arabistan', 'Mısır', 'Nijerya', 'Rusya', 'Ukrayna',
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
    company_name?: string;
    country?: string;
    contact?: string;
    website?: string;
    source?: string;
    product_match?: string;
    relevance_score?: number;
    url_status?: number | null;
    raw_data?: Record<string, unknown>;
    // Eski format uyumluluğu
    title?: string;
    name?: string;
    email?: string;
    phone?: string;
    url?: string;
    category?: string;
    gtip_code?: string;
    oem_code?: string;
}

interface SourceResult {
    results: SearchResult[];
    error: string | null;
}

interface SearchResponse {
    results: SearchResult[];
    by_source: Record<string, SourceResult>;
    total: number;
    sources_searched: string[];
}

function getDisplayName(r: SearchResult) { return r.company_name || r.title || r.name || '—'; }
function getDisplayCountry(r: SearchResult) { return r.country || '—'; }
function getDisplayContact(r: SearchResult) { return r.contact || r.email || r.phone || '—'; }
function getDisplayLink(r: SearchResult) { return r.website || r.url || null; }
function getDisplaySource(r: SearchResult) { return r.source || r.category || '—'; }
function getScore(r: SearchResult) { return r.relevance_score ?? 50; }

function ScoreBadge({ score }: { score: number }) {
    const color = score >= 70 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#64748b';
    return (
        <span style={{ color, fontWeight: 700, fontSize: 12 }}>{score}</span>
    );
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
    const [selectedEngines, setSelectedEngines] = useState<string[]>(SEARCH_ENGINES.slice(0, 3));
    const [selectedDBs, setSelectedDBs] = useState<string[]>(DB_SOURCES.slice(0, 4));

    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState<SearchResponse | null>(null);
    const [error, setError] = useState('');

    // Filtreler
    const [filterSource, setFilterSource] = useState('');
    const [filterCountry, setFilterCountry] = useState('');
    const [sortBy, setSortBy] = useState<'relevance' | 'source' | 'country'>('relevance');

    const toggleItem = (arr: string[], setArr: (v: string[]) => void, item: string) => {
        setArr(arr.includes(item) ? arr.filter(i => i !== item) : [...arr, item]);
    };

    const handleSearch = async () => {
        if (!formData.product.trim()) {
            setError('Lütfen en az ürün adı girin');
            return;
        }
        if (selectedEngines.length === 0 && selectedDBs.length === 0) {
            setError('En az bir kaynak seçin');
            return;
        }

        setLoading(true);
        setError('');
        setResponse(null);
        setFilterSource('');
        setFilterCountry('');

        try {
            const res = await api.post('/search/customers', {
                product_name: formData.product.trim(),
                gtip_code: formData.gtip.trim(),
                oem_no: formData.oemNo.trim(),
                target_country: formData.country || '',
                search_language: LANGUAGE_MAP[formData.language] || 'en',
                related_sectors: formData.linkedSectors.trim(),
                competitor_brands: formData.competitors.trim(),
                search_engines: selectedEngines,
                db_sources: selectedDBs,
                max_results: 100,
            });
            setResponse(res.data as SearchResponse);
        } catch (e: unknown) {
            const err = e as { response?: { data?: { detail?: string } } };
            setError(err?.response?.data?.detail || 'Arama sırasında hata oluştu');
        } finally {
            setLoading(false);
        }
    };

    // Client-side filtrele + sırala
    const filteredResults = useMemo(() => {
        if (!response) return [];
        let items = [...response.results];
        if (filterSource) items = items.filter(r => getDisplaySource(r) === filterSource);
        if (filterCountry) items = items.filter(r => (r.country || '').toLowerCase().includes(filterCountry.toLowerCase()));
        if (sortBy === 'relevance') items.sort((a, b) => getScore(b) - getScore(a));
        else if (sortBy === 'source') items.sort((a, b) => getDisplaySource(a).localeCompare(getDisplaySource(b)));
        else if (sortBy === 'country') items.sort((a, b) => getDisplayCountry(a).localeCompare(getDisplayCountry(b)));
        return items;
    }, [response, filterSource, filterCountry, sortBy]);

    // Kaynak listesi (filtre için)
    const availableSources = useMemo(() => {
        if (!response) return [];
        return [...new Set(response.results.map(r => getDisplaySource(r)).filter(Boolean))];
    }, [response]);

    const handleExcel = async () => {
        if (!response || response.total === 0) { alert('Önce arama yapın'); return; }
        // CSV export
        const headers = ['Şirket', 'Ülke', 'Kaynak', 'İletişim', 'Website', 'Skor', 'Ürün Eşleşmesi'];
        const rows = filteredResults.map(r => [
            getDisplayName(r), getDisplayCountry(r), getDisplaySource(r),
            getDisplayContact(r), getDisplayLink(r) || '', getScore(r), r.product_match || ''
        ]);
        const csv = [headers, ...rows].map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `musteri_arama_${formData.product}_${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

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
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ürün / Parça Adı *</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: piston, brake pad, gear box..."
                                    value={formData.product}
                                    onChange={e => setFormData({ ...formData, product: e.target.value })}
                                    onKeyDown={e => e.key === 'Enter' && handleSearch()}
                                />
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">GTİP Kodu</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: 8409.91"
                                    value={formData.gtip}
                                    onChange={e => setFormData({ ...formData, gtip: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">TradeMap ve UN Comtrade için kullanılır</span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">OEM No (Opsiyonel)</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: 12345-ABC-67890"
                                    value={formData.oemNo}
                                    onChange={e => setFormData({ ...formData, oemNo: e.target.value })}
                                />
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
                                    <option value="auto">🤖 Otomatik</option>
                                    {Object.keys(LANGUAGE_MAP).map(l => <option key={l} value={l}>{l}</option>)}
                                </select>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Bağlı Sektörler</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                    placeholder="Örn: otomotiv, makine imalat..."
                                    value={formData.linkedSectors}
                                    onChange={e => setFormData({ ...formData, linkedSectors: e.target.value })}
                                />
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
                                <p className="text-[#64748b] text-[13px] mt-2">Görüntü işleme özelliği yakında aktif olacak</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Search Engines */}
                <div className="mt-4 p-5 bg-[#0a162888] border border-[#1e3a5f33] rounded-xl mb-4">
                    <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-semibold text-[#94a3b8] m-0">🌐 Taranacak Arama Motorları</h4>
                        <div className="flex gap-2">
                            <button onClick={() => setSelectedEngines(SEARCH_ENGINES)} className="text-xs text-[#00e5a0] hover:underline">Tümünü Seç</button>
                            <span className="text-[#475569]">|</span>
                            <button onClick={() => setSelectedEngines([])} className="text-xs text-[#64748b] hover:underline">Temizle</button>
                        </div>
                    </div>
                    <div className="flex flex-wrap gap-2.5">
                        {SEARCH_ENGINES.map(e => (
                            <label key={e} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[13px] cursor-pointer transition-colors ${selectedEngines.includes(e) ? 'bg-[#00e5a015] border border-[#00e5a033] text-[#00e5a0]' : 'bg-[#0d1f35] border border-transparent text-[#cbd5e1] hover:bg-[#1e3a5f]'}`}>
                                <input
                                    type="checkbox"
                                    checked={selectedEngines.includes(e)}
                                    onChange={() => toggleItem(selectedEngines, setSelectedEngines, e)}
                                    className="accent-[#00e5a0] sr-only"
                                />
                                {selectedEngines.includes(e) ? '✓ ' : ''}{e}
                            </label>
                        ))}
                    </div>
                </div>

                {/* DB Sources */}
                <div className="p-5 bg-[#0a162888] border border-[#1e3a5f33] rounded-xl">
                    <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-semibold text-[#94a3b8] m-0">📊 Dış Ticaret Veritabanları</h4>
                        <div className="flex gap-2">
                            <button onClick={() => setSelectedDBs(DB_SOURCES)} className="text-xs text-[#0ea5e9] hover:underline">Tümünü Seç</button>
                            <span className="text-[#475569]">|</span>
                            <button onClick={() => setSelectedDBs([])} className="text-xs text-[#64748b] hover:underline">Temizle</button>
                        </div>
                    </div>
                    <div className="flex flex-wrap gap-2.5">
                        {DB_SOURCES.map(s => (
                            <label key={s} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[13px] cursor-pointer transition-colors ${selectedDBs.includes(s) ? 'bg-[#0ea5e915] border border-[#0ea5e933] text-[#0ea5e9]' : 'bg-[#0d1f35] border border-transparent text-[#cbd5e1] hover:bg-[#1e3a5f]'}`}>
                                <input
                                    type="checkbox"
                                    checked={selectedDBs.includes(s)}
                                    onChange={() => toggleItem(selectedDBs, setSelectedDBs, s)}
                                    className="accent-[#0ea5e9] sr-only"
                                />
                                {selectedDBs.includes(s) ? '✓ ' : ''}{s}
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
                <div className="flex gap-3 mt-6 flex-wrap">
                    <button
                        onClick={handleSearch}
                        disabled={loading}
                        className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer hover:brightness-110 disabled:opacity-50 transition-all"
                    >
                        {loading ? `⏳ Aranıyor... (${selectedEngines.length + selectedDBs.length} kaynak)` : '🚀 Aramayı Başlat'}
                    </button>
                    {response && response.total > 0 && (
                        <button
                            onClick={handleExcel}
                            className="px-8 py-3.5 bg-transparent border border-[#1e3a5f] rounded-xl text-[#94a3b8] text-[15px] font-medium cursor-pointer hover:bg-[#1e3a5f22] transition-all"
                        >
                            📊 CSV İndir
                        </button>
                    )}
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="mt-6 p-5 bg-[#0d1f35] border border-[#1e3a5f44] rounded-xl">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-4 h-4 rounded-full bg-[#00e5a0] animate-pulse" />
                            <span className="text-[#94a3b8] text-sm">
                                {selectedEngines.concat(selectedDBs).join(', ')} kaynakları paralel taranıyor...
                            </span>
                        </div>
                        <div className="text-xs text-[#475569]">
                            Tarama tamamlanana kadar bekleyin. Birden fazla kaynak aynı anda çalışıyor.
                        </div>
                    </div>
                )}

                {/* Results */}
                {response && (
                    <div className="mt-8">
                        {/* Özet */}
                        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
                            <h3 className="text-xl font-bold text-[#e2e8f0] m-0">
                                📊 {response.total} Sonuç — {response.sources_searched.length} Kaynak Tarandı
                            </h3>
                            <div className="flex gap-2 flex-wrap">
                                {response.sources_searched.map(src => {
                                    const sd = response.by_source[src];
                                    const count = sd?.results?.length ?? 0;
                                    const hasError = sd?.error;
                                    return (
                                        <span key={src} className={`px-2 py-1 rounded text-xs font-medium ${hasError ? 'bg-red-500/10 text-red-400' : count > 0 ? 'bg-[#00e5a010] text-[#00e5a0]' : 'bg-[#1e3a5f44] text-[#64748b]'}`}>
                                            {src}: {hasError ? '⚠' : count}
                                        </span>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Filtreler */}
                        {response.total > 0 && (
                            <div className="flex gap-3 mb-4 flex-wrap items-center">
                                <select
                                    className="px-3 py-2 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#94a3b8] text-sm outline-none focus:border-[#00e5a0]"
                                    value={filterSource}
                                    onChange={e => setFilterSource(e.target.value)}
                                >
                                    <option value="">Tüm Kaynaklar</option>
                                    {availableSources.map(s => <option key={s} value={s}>{s}</option>)}
                                </select>
                                <input
                                    className="px-3 py-2 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#94a3b8] text-sm outline-none focus:border-[#00e5a0]"
                                    placeholder="Ülke filtrele..."
                                    value={filterCountry}
                                    onChange={e => setFilterCountry(e.target.value)}
                                />
                                <select
                                    className="px-3 py-2 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#94a3b8] text-sm outline-none focus:border-[#00e5a0]"
                                    value={sortBy}
                                    onChange={e => setSortBy(e.target.value as 'relevance' | 'source' | 'country')}
                                >
                                    <option value="relevance">Skor ↓</option>
                                    <option value="source">Kaynak A-Z</option>
                                    <option value="country">Ülke A-Z</option>
                                </select>
                                <span className="text-xs text-[#64748b]">{filteredResults.length} sonuç gösteriliyor</span>
                            </div>
                        )}

                        {filteredResults.length === 0 ? (
                            <div className="bg-[#0d1f35] border border-[#1e3a5f44] rounded-2xl p-8 text-center text-[#64748b]">
                                <div className="text-4xl mb-3">🔍</div>
                                <p>Sonuç bulunamadı. Filtre kriterlerini değiştirin veya ScraperAPI key ekleyin.</p>
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
                                            <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44]">Skor</th>
                                            <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44]">Link</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredResults.map((r, i) => {
                                            const link = getDisplayLink(r);
                                            const isVerified = r.url_status === 200;
                                            const hasLink = !!link;
                                            return (
                                                <tr key={i} className="border-b border-[#1e3a5f22] last:border-0 hover:bg-[#0d1f3522] transition-colors">
                                                    <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                        <strong>{getDisplayName(r)}</strong>
                                                        {r.gtip_code && <span className="ml-2 px-1.5 py-0.5 bg-[#00e5a011] text-[#00e5a0] rounded text-xs">GTİP: {r.gtip_code}</span>}
                                                        {r.oem_code && <span className="ml-2 px-1.5 py-0.5 bg-[#0ea5e911] text-[#0ea5e9] rounded text-xs">OEM: {r.oem_code}</span>}
                                                        {r.product_match && <div className="text-xs text-[#475569] mt-0.5">🔗 {r.product_match}</div>}
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-[#cbd5e1]">{getDisplayCountry(r)}</td>
                                                    <td className="px-4 py-3 text-sm">
                                                        <span className="px-2 py-0.5 bg-[#8b5cf611] text-[#8b5cf6] rounded text-xs">{getDisplaySource(r)}</span>
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-[#94a3b8] font-mono text-xs">{getDisplayContact(r)}</td>
                                                    <td className="px-4 py-3 text-sm text-center">
                                                        <ScoreBadge score={getScore(r)} />
                                                    </td>
                                                    <td className="px-4 py-3 text-sm">
                                                        {hasLink && isVerified ? (
                                                            <a href={link!} target="_blank" rel="noopener noreferrer"
                                                                className="text-[#00e5a0] hover:underline text-xs">
                                                                🔗 Görüntüle
                                                            </a>
                                                        ) : hasLink && !isVerified ? (
                                                            <span className="px-1.5 py-0.5 bg-yellow-500/10 text-yellow-500 rounded text-xs">⚠ Doğrulanamadı</span>
                                                        ) : (
                                                            <span className="text-[#475569] text-xs">—</span>
                                                        )}
                                                    </td>
                                                </tr>
                                            );
                                        })}
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
