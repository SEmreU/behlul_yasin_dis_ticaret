'use client';

import DashboardLayout from '@/components/dashboard/DashboardLayout';

export default function ChinaPage() {
    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🇨🇳 Çin Pazarı Özel Arama</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Çin&apos;den tedarikçi bulmak isteyenler için özelleştirilmiş arama motoru
                    </p>
                </div>

                {/* Info Box */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    Çin hemen hemen her sektörde rekabetçi fiyat sunuyor. Bu modül Baidu, 1688.com, Made-in-China ve Alibaba entegrasyonu ile
                    Çinli tedarikçileri hızlıca bulmanızı sağlar.
                </div>

                {/* Form Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ürün Adı (İngilizce)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: hydraulic cylinder"
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ürün Adı (Çince - Opsiyonel)</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="液压缸"
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Minimum Sipariş Miktarı</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: 100 adet"
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Sertifika Gereksinimi</label>
                        <select className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none">
                            <option>Hepsi</option>
                            <option>ISO 9001</option>
                            <option>CE</option>
                            <option>SGS Denetimli</option>
                        </select>
                    </div>
                </div>

                <button className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer">
                    🔍 Çin Tedarikçi Ara
                </button>
            </div>
        </DashboardLayout>
    );
}
