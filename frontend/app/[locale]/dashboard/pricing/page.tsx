'use client';

import DashboardLayout from '@/components/dashboard/DashboardLayout';

const PLANS = [
    {
        name: 'Modül 1',
        subtitle: 'Ziyaretçi Takibi',
        setup: '2,000',
        monthly: '30',
        features: ['Gerçek zamanlı ziyaretçi tespiti', 'IP & konum analizi', 'Firma eşleştirme', 'Bildirim sistemi'],
        color: '#00e5a0',
    },
    {
        name: 'Modül 2',
        subtitle: 'Müşteri Arama',
        setup: '500',
        monthly: '10',
        features: ['AI destekli arama', 'Çoklu arama motoru', 'Görsel arama', 'Excel çıktı'],
        color: '#0ea5e9',
    },
    {
        name: 'Tam Paket',
        subtitle: 'Tüm Modüller',
        setup: '4,000',
        monthly: '100',
        features: ['9 modülün tamamı', 'Sınırsız sorgu', 'Öncelikli destek', 'API erişimi', 'Özel eğitim'],
        color: '#a855f7',
        popular: true,
    },
];

export default function PricingPage() {
    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">💎 Fiyatlandırma</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        İhtiyacınıza göre modül bazlı veya tam paket seçin
                    </p>
                </div>

                {/* Pricing Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    {PLANS.map((p, i) => (
                        <div
                            key={i}
                            className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] rounded-[20px] p-7 relative text-center"
                            style={{
                                border: p.popular ? `1.5px solid ${p.color}` : '1.5px solid #1e3a5f',
                            }}
                        >
                            {p.popular && (
                                <div
                                    className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-[20px] text-xs font-semibold text-[#0a1628]"
                                    style={{ background: p.color }}
                                >
                                    En Popüler
                                </div>
                            )}
                            <h3 className="text-[22px] font-bold m-0 mb-1" style={{ color: p.color }}>
                                {p.name}
                            </h3>
                            <p className="text-sm text-[#64748b] m-0 mb-6">{p.subtitle}</p>
                            <div className="mb-7">
                                <div>
                                    <span className="text-[28px] font-bold text-[#e2e8f0]">${p.setup}</span>
                                    <span className="text-sm text-[#64748b]"> kurulum</span>
                                </div>
                                <div className="mt-2">
                                    <span className="text-4xl font-bold" style={{ color: p.color }}>
                                        ${p.monthly}
                                    </span>
                                    <span className="text-sm text-[#64748b]">/ay</span>
                                </div>
                            </div>
                            <div className="text-left mb-7">
                                {p.features.map((f, j) => (
                                    <div
                                        key={j}
                                        className="py-2 border-b border-[#1e3a5f22] last:border-0 text-sm text-[#94a3b8] flex items-center gap-2"
                                    >
                                        <span style={{ color: p.color }}>✓</span> {f}
                                    </div>
                                ))}
                            </div>
                            <button
                                className="w-full py-3.5 rounded-xl text-[15px] font-semibold cursor-pointer transition-all"
                                style={{
                                    background: p.popular ? p.color : 'transparent',
                                    color: p.popular ? '#0a1628' : p.color,
                                    border: `1.5px solid ${p.color}`,
                                }}
                            >
                                Başvur
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </DashboardLayout>
    );
}
