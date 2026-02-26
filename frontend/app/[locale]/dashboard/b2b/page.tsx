'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import ExcelExportButton from '@/components/ExcelExportButton';
import { exportMarketplaceToExcel, exportRFQsToExcel } from '@/lib/api-helpers';

const B2B_PLATFORMS = [
    { id: 'tradekey', name: 'TradeKey', region: 'Global', desc: 'RFQ tarama, alım talepleri', color: '#0ea5e9', type: 'rfq' },
    { id: 'ecplaza', name: 'ECPlaza', region: 'Güney Kore', desc: 'Kore pazarı, Asya tedarikçileri', color: '#8b5cf6', type: 'b2b' },
    { id: 'eworldtrade', name: 'eWorldTrade', region: 'Global', desc: 'Global ticaret, RFQ desteği', color: '#10b981', type: 'rfq' },
    { id: 'indiamart', name: 'IndiaMART', region: 'Hindistan', desc: 'Hindistan\'ın en büyüğü', color: '#f59e0b', type: 'b2b' },
    { id: 'tradeindia', name: 'TradeIndia', region: 'Hindistan', desc: 'İhracatçı veritabanı', color: '#06b6d4', type: 'b2b' },
    { id: 'ec21', name: 'EC21', region: 'Global', desc: '7M+ ürün, OEM arama', color: '#a855f7', type: 'b2b' },
    { id: 'kompass', name: 'Kompass', region: 'Avrupa', desc: 'Avrupa firmaları, yetkili mail', color: '#f97316', type: 'directory' },
    { id: 'thomasnet', name: 'Thomasnet', region: 'Kuzey Amerika', desc: 'ABD/Kanada üreticileri', color: '#e11d48', type: 'directory' },
    { id: 'alibaba', name: 'Alibaba', region: 'Çin & Global', desc: 'En büyük B2B platformu', color: '#ff6600', type: 'b2b' },
    { id: 'made-in-china', name: 'Made-in-China', region: 'Çin', desc: 'Çin kaynaklı üreticiler', color: '#e11d48', type: 'b2b' },
    { id: 'dhgate', name: 'DHgate', region: 'Çin & Global', desc: 'Düşük MOQ, dropshipping', color: '#06b6d4', type: 'b2b' },
];

export default function B2BPage() {
    const [activeTab, setActiveTab] = useState<'search' | 'rfq'>('search');
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['alibaba', 'tradekey', 'indiamart']);
    const [searchQuery, setSearchQuery] = useState('');
    const [category, setCategory] = useState('');
    const [oemNo, setOemNo] = useState('');
    const [gtipCode, setGtipCode] = useState('');

    const [searchResults, setSearchResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [excelLoading, setExcelLoading] = useState(false);

    const togglePlatform = (platformId: string) => {
        setSelectedPlatforms(prev =>
            prev.includes(platformId)
                ? prev.filter(id => id !== platformId)
                : [...prev, platformId]
        );
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            alert('Lütfen arama terimi girin');
            return;
        }

        setLoading(true);
        try {
            const endpoint = activeTab === 'rfq'
                ? 'http://localhost:8000/api/v1/marketplace/search-rfqs'
                : 'http://localhost:8000/api/v1/marketplace/search-all';

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
                body: JSON.stringify({
                    query: searchQuery,
                    platforms: selectedPlatforms,
                    search_type: activeTab,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setSearchResults(data);
            } else {
                alert('Arama başarısız oldu');
            }
        } catch (error) {
            console.error('Search error:', error);
            alert('Arama sırasında hata oluştu');
        } finally {
            setLoading(false);
        }
    };

    const handleExportExcel = async () => {
        if (!searchQuery.trim()) {
            alert('Önce arama yapın');
            return;
        }

        setExcelLoading(true);
        try {
            if (activeTab === 'rfq') {
                await exportRFQsToExcel(searchQuery);
            } else {
                await exportMarketplaceToExcel(searchQuery, selectedPlatforms);
            }
            alert('Excel dosyası başarıyla indirildi!');
        } catch (e) {
            console.error('Export error:', e);
            alert('Excel indirme başarısız oldu.');
        } finally {
            setExcelLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7 flex justify-between items-start">
                    <div>
                        <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🌐 B2B Platform Tarama</h2>
                        <p className="text-[15px] text-[#64748b] mt-2">
                            10 global B2B pazaryerinden ürün ve RFQ taraması yapın
                        </p>
                    </div>
                    {searchResults && (
                        <ExcelExportButton
                            onClick={handleExportExcel}
                            loading={excelLoading}
                        />
                    )}
                </div>

                {/* Tabs */}
                <div className="flex gap-2 mb-6">
                    <button
                        onClick={() => setActiveTab('search')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${activeTab === 'search'
                            ? 'bg-gradient-to-br from-[#00e5a0] to-[#00b87a] text-[#0a1628]'
                            : 'bg-transparent border border-[#1e3a5f] text-[#94a3b8] hover:bg-[#0d1f35]'
                            }`}
                    >
                        🔍 Ürün Arama
                    </button>
                    <button
                        onClick={() => setActiveTab('rfq')}
                        className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${activeTab === 'rfq'
                            ? 'bg-gradient-to-br from-[#00e5a0] to-[#00b87a] text-[#0a1628]'
                            : 'bg-transparent border border-[#1e3a5f] text-[#94a3b8] hover:bg-[#0d1f35]'
                            }`}
                    >
                        📋 RFQ Tarama
                    </button>
                </div>

                {/* B2B Platforms Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-6">
                    {B2B_PLATFORMS.map((p) => {
                        const isSelected = selectedPlatforms.includes(p.id);
                        return (
                            <div
                                key={p.id}
                                onClick={() => togglePlatform(p.id)}
                                className={`bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border rounded-[14px] p-4 cursor-pointer transition-all ${isSelected
                                    ? 'border-[#00e5a0] shadow-lg shadow-[#00e5a022]'
                                    : 'border-[#1e3a5f44] hover:border-[#1e3a5f]'
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h4 className="text-base font-semibold m-0 mb-1" style={{ color: p.color }}>
                                            {p.name}
                                        </h4>
                                        <span className="text-xs text-[#64748b]">{p.region}</span>
                                    </div>
                                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${isSelected ? 'bg-[#00e5a0] border-[#00e5a0]' : 'border-[#1e3a5f]'
                                        }`}>
                                        {isSelected && <span className="text-[#0a1628] text-xs">✓</span>}
                                    </div>
                                </div>
                                <p className="text-[13px] text-[#94a3b8] mt-2.5 mb-0">{p.desc}</p>
                            </div>
                        );
                    })}
                </div>

                {/* Search Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            {activeTab === 'rfq' ? 'RFQ Arama Terimi' : 'Aranacak Ürün'}
                        </label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder={activeTab === 'rfq' ? 'Örn: automotive parts' : 'Ürün adını girin...'}
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Kategori</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: Otomotiv, Makine, Tekstil..."
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">OEM No (Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: 12345-ABC-67890"
                            value={oemNo}
                            onChange={(e) => setOemNo(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">GTİP Kodu (Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: 8708.29.10.00"
                            value={gtipCode}
                            onChange={(e) => setGtipCode(e.target.value)}
                        />
                    </div>
                </div>

                <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer disabled:opacity-50"
                >
                    {loading ? '⏳ Taranıyor...' : `🔎 ${selectedPlatforms.length} Platformu Tara`}
                </button>

                {/* Results Table */}
                {searchResults && (
                    <div className="mt-8">
                        <h3 className="text-xl font-bold text-[#e2e8f0] mb-4">
                            📊 Sonuçlar: {searchResults.total_results || searchResults.total_rfqs || 0} kayıt bulundu
                        </h3>

                        <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl overflow-hidden">
                            <table className="w-full border-collapse">
                                <thead>
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                            Platform
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                            {activeTab === 'rfq' ? 'RFQ Başlığı' : 'Ürün'}
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                            {activeTab === 'rfq' ? 'Firma' : 'Tedarikçi'}
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                            {activeTab === 'rfq' ? 'Ülke' : 'Fiyat'}
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                            Link
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {activeTab === 'rfq' ? (
                                        // RFQ Results
                                        searchResults.rfqs?.map((item: { source: string; title: string; company?: string; country?: string; url: string }, i: number) => (
                                            <tr key={i} className="border-b border-[#1e3a5f22] last:border-0">
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                    <span className="px-2 py-1 bg-[#0ea5e922] text-[#0ea5e9] rounded text-xs">
                                                        {item.source}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                    <strong>{item.title}</strong>
                                                </td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">{item.company || 'N/A'}</td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">{item.country || 'N/A'}</td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                    <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-[#00e5a0] hover:underline">
                                                        🔗 Görüntüle
                                                    </a>
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        // Product Results
                                        Object.entries(searchResults.results || {}).flatMap(([platform, items]: [string, any]) =>
                                            items.map((item: { source?: string; title: string; supplier?: string; company?: string; price?: string; url: string }, i: number) => (
                                                <tr key={`${platform}-${i}`} className="border-b border-[#1e3a5f22] last:border-0">
                                                    <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                        <span className="px-2 py-1 bg-[#0ea5e922] text-[#0ea5e9] rounded text-xs">
                                                            {item.source || platform}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                        <strong>{item.title}</strong>
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-[#cbd5e1]">{item.supplier || item.company || 'N/A'}</td>
                                                    <td className="px-4 py-3 text-sm text-[#cbd5e1]">{item.price || 'N/A'}</td>
                                                    <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-[#00e5a0] hover:underline">
                                                            🔗 Görüntüle
                                                        </a>
                                                    </td>
                                                </tr>
                                            ))
                                        )
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
