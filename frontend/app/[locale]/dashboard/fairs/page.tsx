'use client';

import DashboardLayout from '@/components/dashboard/DashboardLayout';

export default function FairsPage() {
    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🎪 Fuar Katılımcı Analizi</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Fuar katılımcılarını analiz edin, sadece sizinle eşleşen firmaları bulun
                    </p>
                </div>

                {/* Info Box */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong>Örnek Senaryo:</strong> Konya'da piston üreten bir firma olarak Automechanika fuarlarına (Almanya, Dubai, Brezilya, Çin, ABD)
                    katılmak maliyetli. Bu modül katılımcı listelerini tarayarak sadece sizinle eşleşen firmaları Excel olarak verir.
                </div>

                {/* Fair Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl p-6">
                        <h4 className="text-base font-semibold text-[#e2e8f0] m-0 mb-5">Fuar Bilgileri</h4>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Fuar Katılımcı Listesi</label>
                                <div className="border border-[#1e3a5f] rounded-lg p-3.5 text-center cursor-pointer hover:border-[#00e5a044] bg-[#0a1628]">
                                    <span className="text-sm text-[#64748b]">📎 Katılımcı listesi yükle (Excel / PDF)</span>
                                </div>
                            </div>
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">veya Firma Web Site Linkleri</label>
                                <textarea
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none resize-y"
                                    rows={4}
                                    placeholder="www.firma1.com&#10;www.firma2.com"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl p-6">
                        <h4 className="text-base font-semibold text-[#e2e8f0] m-0 mb-5">Eşleştirme Kriterleri</h4>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ürün / Sektör</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: piston, engine parts"
                                />
                            </div>
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Anahtar Kelimeler</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: automotive, spare parts, OEM"
                                />
                            </div>
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">GTİP Kodu</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: 8409.91"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <button className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer">
                    🔎 Katılımcıları Analiz Et
                </button>
            </div>
        </DashboardLayout>
    );
}
