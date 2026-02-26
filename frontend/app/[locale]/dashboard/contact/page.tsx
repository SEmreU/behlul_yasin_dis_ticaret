'use client';

import DashboardLayout from '@/components/dashboard/DashboardLayout';

export default function ContactPage() {
    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">📧 Yetkili İletişim Bulucu</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Web sitelerindeki info@ adresleri yerine gerçek yetkili e-posta adreslerini bulun
                    </p>
                </div>

                {/* Info Box */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong>Problem:</strong> Firmaların iletişim sayfalarında genellikle info@firma.com gibi genel adresler bulunur.
                    Bu modül, <strong>purchasing@</strong>, <strong>manager@</strong> veya kişisel yetkili e-posta adreslerini web sitesi verilerinden çıkarır.
                </div>

                {/* Form */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    <div className="col-span-2">
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            Firma Web Siteleri (her satıra bir tane)
                        </label>
                        <textarea
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none resize-y"
                            rows={6}
                            placeholder="www.firma1.com&#10;www.firma2.de&#10;www.firma3.co.uk"
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            veya Excel Dosyası Yükle
                        </label>
                        <div className="border border-[#1e3a5f] rounded-lg p-3.5 text-center cursor-pointer hover:border-[#00e5a044] bg-[#0a1628]">
                            <span className="text-sm text-[#64748b]">📎 Excel yükle (.xlsx)</span>
                        </div>
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            Aranan Pozisyon
                        </label>
                        <div className="space-y-2">
                            {['Purchasing Manager', 'Sales Manager', 'General Manager', 'Owner/CEO', 'Import Manager'].map((p) => (
                                <label key={p} className="flex items-center gap-1.5 text-sm text-[#cbd5e1] cursor-pointer">
                                    <input type="checkbox" defaultChecked className="accent-[#00e5a0]" />
                                    {p}
                                </label>
                            ))}
                        </div>
                    </div>
                </div>

                <button className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer">
                    🔍 Yetkili Bilgilerini Bul
                </button>
            </div>
        </DashboardLayout>
    );
}
