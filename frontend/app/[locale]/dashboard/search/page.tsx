'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';

const COUNTRIES = [
    'Almanya', 'İngiltere', 'Fransa', 'İtalya', 'İspanya', 'Hollanda', 'Belçika',
    'Avusturya', 'İsviçre', 'Polonya', 'Çekya', 'Romanya', 'Bulgaristan', 'Yunanistan',
];

const LANGUAGES = [
    'İngilizce', 'Almanca', 'Fransızca', 'İspanyolca', 'İtalyanca', 'Portekizce',
    'Rusça', 'Arapça', 'Çince (Mandarin)', 'Japonca', 'Korece', 'Hintçe', 'Türkçe',
];

const DB_SOURCES = [
    'TradeAtlas', 'ImportGenius', 'Trademo Intel', 'Panjiva', 'Global Buyers Online',
    'Europages', 'TradeKey', 'TradeMap', 'UN Comtrade'
];

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
        // 7 dilde parça ismi
        productNameEn: '',
        productNameDe: '',
        productNameFr: '',
        productNameEs: '',
        productNameIt: '',
        productNameRu: '',
        productNameZh: '',
    });

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
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

                {/* Form Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    {searchType === 'text' ? (
                        <>
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                                    Ürün / Parça Adı
                                </label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: piston, brake pad, gear box..."
                                    value={formData.product}
                                    onChange={(e) => setFormData({ ...formData, product: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">
                                    IATE + Cambridge Sözlük doğrulaması yapılır
                                </span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                                    GTİP Kodu
                                </label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: 8409.91"
                                    value={formData.gtip}
                                    onChange={(e) => setFormData({ ...formData, gtip: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">
                                    Bağlı / Tamamlayıcı GTİP'ler otomatik sorgulanır
                                </span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                                    OEM No (Opsiyonel)
                                </label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: 12345-ABC-67890"
                                    value={formData.oemNo}
                                    onChange={(e) => setFormData({ ...formData, oemNo: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">
                                    OEM numarası ile doğrudan eşleşme
                                </span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                                    Hedef Ülke
                                </label>
                                <select
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    value={formData.country}
                                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                                >
                                    <option value="">Ülke seçin...</option>
                                    <option value="all">🌍 Tüm Ülkeler</option>
                                    {COUNTRIES.map((c) => (
                                        <option key={c} value={c}>{c}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                                    Arama Dili
                                </label>
                                <select
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    value={formData.language}
                                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                                >
                                    <option value="">Dil seçin...</option>
                                    <option value="auto">🤖 Otomatik (Ülkeye göre)</option>
                                    {LANGUAGES.map((l) => (
                                        <option key={l} value={l}>{l}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                                    Bağlı Sektörler
                                </label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: hırdavat, otomotiv yedek parça..."
                                    value={formData.linkedSectors}
                                    onChange={(e) => setFormData({ ...formData, linkedSectors: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">
                                    İkincil ithalatçıları yakalamak için tamamlayıcı sektörler
                                </span>
                            </div>

                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                                    Rakip Firmalar / Markalar
                                </label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: Mahle, Federal Mogul, NPR..."
                                    value={formData.competitors}
                                    onChange={(e) => setFormData({ ...formData, competitors: e.target.value })}
                                />
                                <span className="block text-xs text-[#475569] mt-1.5">
                                    Rakip markaları aratan müşteriler de taranır
                                </span>
                            </div>
                        </>
                    ) : (
                        <div className="col-span-2">
                            <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                                Ürün Görseli Yükle
                            </label>
                            <div className="border-2 border-dashed border-[#1e3a5f] rounded-2xl p-10 text-center cursor-pointer hover:border-[#00e5a044]">
                                <div className="text-5xl mb-3">📸</div>
                                <p className="text-[#94a3b8] m-0">Ürün görselini sürükleyin veya tıklayarak seçin</p>
                                <p className="text-[#64748b] text-[13px] mt-2">
                                    Görüntü işleme ile eşleşen web siteleri taranacaktır
                                </p>
                                <button className="mt-4 px-6 py-2.5 bg-[#1e3a5f] border-none rounded-lg text-[#e2e8f0] text-sm cursor-pointer hover:bg-[#2a4a6f]">
                                    Dosya Seç
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Search Engines */}
                <div className="mt-6 p-5 bg-[#0a162888] border border-[#1e3a5f33] rounded-xl">
                    <h4 className="text-sm font-semibold text-[#94a3b8] m-0 mb-3">
                        Taranacak Arama Motorları
                    </h4>
                    <div className="flex flex-wrap gap-2.5">
                        {['Google', 'Yandex', 'Bing', 'Baidu', 'DuckDuckGo', 'Yahoo'].map((e) => (
                            <label key={e} className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0d1f35] rounded-lg text-[13px] text-[#cbd5e1] cursor-pointer">
                                <input type="checkbox" defaultChecked className="accent-[#00e5a0]" />
                                {e}
                            </label>
                        ))}
                    </div>
                </div>

                {/* Database Sources */}
                <div className="mt-5 p-5 bg-[#0a162888] border border-[#1e3a5f33] rounded-xl">
                    <h4 className="text-sm font-semibold text-[#94a3b8] m-0 mb-3">
                        Dış Ticaret Veritabanları
                    </h4>
                    <div className="flex flex-wrap gap-2.5">
                        {DB_SOURCES.map((s) => (
                            <label key={s} className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0d1f35] rounded-lg text-[13px] text-[#cbd5e1] cursor-pointer">
                                <input type="checkbox" defaultChecked className="accent-[#0ea5e9]" />
                                {s}
                            </label>
                        ))}
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 mt-6">
                    <button className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer hover:brightness-110">
                        🚀 Aramayı Başlat
                    </button>
                    <button className="px-8 py-3.5 bg-transparent border border-[#1e3a5f] rounded-xl text-[#94a3b8] text-[15px] font-medium cursor-pointer hover:bg-[#1e3a5f22]">
                        📊 Excel Olarak İndir
                    </button>
                </div>
            </div>
        </DashboardLayout>
    );
}
