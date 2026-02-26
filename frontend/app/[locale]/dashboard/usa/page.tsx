'use client';

import DashboardLayout from '@/components/dashboard/DashboardLayout';

export default function USAPage() {
    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🇺🇸 ABD Pazarı Detaylı Arama</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Amerika'daki ithalatçıları daha detaylı bulun — bilgi yoğunluğunda kaybolmayın
                    </p>
                </div>

                {/* Info Box */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    ABD büyük bir pazar ama bilgi fazlalığı yüzünden doğru müşteriyi bulmak zor. Bu modül ABD'ye özel veri kaynakları
                    (Thomasnet, ImportGenius, Panjiva) ile hedefe yönelik sonuçlar üretir.
                </div>

                {/* Form Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ürün / Sektör</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: auto parts, machinery"
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Eyalet (Opsiyonel)</label>
                        <select className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none">
                            <option>Tüm ABD</option>
                            <option>California</option>
                            <option>Texas</option>
                            <option>Florida</option>
                            <option>New York</option>
                            <option>Michigan</option>
                            <option>Ohio</option>
                            <option>Illinois</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Firma Tipi</label>
                        <select className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none">
                            <option>Hepsi</option>
                            <option>İthalatçı</option>
                            <option>Distribütör</option>
                            <option>OEM Üretici</option>
                            <option>Perakendeci</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">HS Kodu</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Örn: 8409"
                        />
                    </div>
                </div>

                <button className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer">
                    🔍 ABD Müşteri Ara
                </button>
            </div>
        </DashboardLayout>
    );
}
