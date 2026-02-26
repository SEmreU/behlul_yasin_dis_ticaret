'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import ExcelExportButton from '@/components/ExcelExportButton';
import { exportMapsToExcel } from '@/lib/api-helpers';

const COUNTRIES = ['Almanya', 'İngiltere', 'Fransa', 'İtalya', 'İspanya', 'Hollanda'];
const LANGUAGES = ['İngilizce', 'Almanca', 'Fransızca', 'İspanyolca', 'İtalyanca'];

export default function MapsPage() {
    const [formData, setFormData] = useState({
        country: '',
        language: '',
        keyword1: '',
        keyword2: '',
        keyword3: '',
        city: '',
    });
    const [excelLoading, setExcelLoading] = useState(false);

    const handleExportExcel = async () => {
        if (!formData.country || !formData.keyword1) {
            alert('Lütfen en az ülke ve 1. anahtar kelimeyi girin');
            return;
        }

        setExcelLoading(true);
        try {
            const keywords = [formData.keyword1, formData.keyword2, formData.keyword3]
                .filter(k => k.trim())
                .join(',');

            await exportMapsToExcel(formData.country, keywords, formData.city);
            alert('Excel dosyası başarıyla indirildi!');
        } catch (error) {
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
                        <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🗺️ Harita Araştırma Modülü</h2>
                        <p className="text-[15px] text-[#64748b] mt-2">
                            Haritalarda konumu olan firmaları ülke ülke arayın ve Excel listesi olarak indirin
                        </p>
                    </div>
                </div>

                {/* Info Box */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong>Neden Harita Araması?</strong> Bazı firmaların web sitesi olmayabiliyor ama haritalarda konumu ve iletişim bilgileri mevcut olabiliyor.
                    Bu modül ile o firmalara da ulaşabilirsiniz.
                </div>

                {/* Form Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Hedef Ülke</label>
                        <select
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            value={formData.country}
                            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                        >
                            <option value="">Ülke seçin...</option>
                            {COUNTRIES.map((c) => <option key={c} value={c}>{c}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Arama Dili</label>
                        <select
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            value={formData.language}
                            onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                        >
                            <option value="">Dil seçin...</option>
                            {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
                        </select>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Anahtar Kelime 1</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: automotive"
                            value={formData.keyword1}
                            onChange={(e) => setFormData({ ...formData, keyword1: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Anahtar Kelime 2</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: spare parts"
                            value={formData.keyword2}
                            onChange={(e) => setFormData({ ...formData, keyword2: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Anahtar Kelime 3</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: engine components"
                            value={formData.keyword3}
                            onChange={(e) => setFormData({ ...formData, keyword3: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Şehir / Bölge (Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: Birmingham"
                            value={formData.city}
                            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                        />
                    </div>
                </div>

                {/* Map Preview */}
                <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl overflow-hidden mb-6">
                    <div className="h-[300px] flex flex-col items-center justify-center">
                        <svg width="120" height="120" viewBox="0 0 120 120" fill="none" className="mb-4">
                            <circle cx="60" cy="60" r="55" stroke="#1e3a5f" strokeWidth="2" fill="#0d1f35" />
                            <ellipse cx="60" cy="60" rx="55" ry="20" stroke="#1e3a5f" strokeWidth="1" />
                            <line x1="60" y1="5" x2="60" y2="115" stroke="#1e3a5f" strokeWidth="1" />
                            {[
                                [35, 30], [75, 40], [50, 55], [80, 65]
                            ].map(([x, y], i) => (
                                <circle key={i} cx={x} cy={y} r="3" fill="#00e5a0" opacity="0.8" />
                            ))}
                        </svg>
                        <p className="text-[#64748b]">Arama başlatıldığında harita burada görünecek</p>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                    <button className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer">
                        🗺️ Haritada Ara
                    </button>
                    <ExcelExportButton
                        onClick={handleExportExcel}
                        loading={excelLoading}
                    />
                </div>
            </div>
        </DashboardLayout>
    );
}
