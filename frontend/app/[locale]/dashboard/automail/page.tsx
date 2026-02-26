'use client';

import DashboardLayout from '@/components/dashboard/DashboardLayout';

export default function AutoMailPage() {
    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">✉️ Otomatik Mail Gönderimi</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Bulunan müşterilere AI destekli kişiselleştirilmiş tanıtım mailleri gönderin
                    </p>
                </div>

                {/* Warning Box */}
                <div className="bg-[#f59e0b08] border border-[#f59e0b44] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong>⚠️ Anti-Spam Koruması:</strong> Her mail benzersiz içerikle oluşturulur, gönderim zamanları dağıtılır
                    ve domain reputation korunur. Mailler spam'a düşmez.
                </div>

                {/* Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Gönderici Adı</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="Firma Adınız"
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Gönderici E-posta</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                            placeholder="export@firmaniz.com"
                        />
                    </div>
                    <div className="col-span-2">
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Mail Şablonu</label>
                        <textarea
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none resize-y"
                            rows={8}
                            placeholder="Dear {name},&#10;&#10;We are a leading manufacturer of {product} based in Turkey...&#10;&#10;Best regards,&#10;{sender_name}"
                        />
                        <span className="block text-xs text-[#475569] mt-1.5">
                            Değişkenler: {'{name}, {company}, {product}, {country}'}
                        </span>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Katalog Ekle</label>
                        <div className="border border-[#1e3a5f] rounded-lg p-3.5 text-center cursor-pointer hover:border-[#00e5a044] bg-[#0a1628]">
                            <span className="text-sm text-[#64748b]">📎 PDF Katalog Yükle</span>
                        </div>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Alıcı Listesi</label>
                        <div className="border border-[#1e3a5f] rounded-lg p-3.5 text-center cursor-pointer hover:border-[#00e5a044] bg-[#0a1628]">
                            <span className="text-sm text-[#64748b]">📎 Excel Liste Yükle</span>
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                    <button className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer">
                        📤 Mail Gönderimini Başlat
                    </button>
                    <button className="px-8 py-3.5 bg-transparent border border-[#1e3a5f] rounded-xl text-[#94a3b8] text-[15px] font-medium cursor-pointer">
                        👁 Önizleme
                    </button>
                </div>
            </div>
        </DashboardLayout>
    );
}
