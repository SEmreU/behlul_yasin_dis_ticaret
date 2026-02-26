'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function GDPRBanner() {
    const [isVisible, setIsVisible] = useState(false);
    const [showDetails, setShowDetails] = useState(false);

    useEffect(() => {
        // LocalStorage'dan kullanıcı tercihini kontrol et
        const gdprAccepted = localStorage.getItem('gdpr_accepted');
        if (!gdprAccepted) {
            setIsVisible(true);
        }
    }, []);

    const handleAccept = () => {
        localStorage.setItem('gdpr_accepted', 'true');
        setIsVisible(false);
    };

    const handleReject = () => {
        localStorage.setItem('gdpr_accepted', 'false');
        setIsVisible(false);
    };

    if (!isVisible) return null;

    return (
        <>
            {/* Overlay */}
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9998]" />

            {/* Banner */}
            <div className="fixed bottom-0 left-0 right-0 z-[9999] p-4 md:p-6">
                <div className="max-w-5xl mx-auto bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f] rounded-2xl shadow-2xl overflow-hidden">
                    <div className="p-6">
                        {/* Header */}
                        <div className="flex items-start gap-3 mb-4">
                            <div className="flex-shrink-0 w-10 h-10 bg-[#00e5a022] rounded-lg flex items-center justify-center text-xl">
                                🔒
                            </div>
                            <div className="flex-1">
                                <h3 className="text-lg font-bold text-[#e2e8f0] mb-1">
                                    KVKK Aydınlatma Metni
                                </h3>
                                <p className="text-sm text-[#94a3b8] leading-relaxed">
                                    Web sitemizi ziyaret ettiğinizde, IP adresiniz ve konum bilgileriniz işlenerek
                                    potansiyel iş fırsatları için firma eşleştirmesi yapılmaktadır.
                                </p>
                            </div>
                        </div>

                        {/* Details Section */}
                        {showDetails && (
                            <div className="bg-[#0a162888] border border-[#1e3a5f44] rounded-lg p-4 mb-4 text-sm text-[#94a3b8] leading-relaxed">
                                <h4 className="font-semibold text-[#e2e8f0] mb-2">Veri İşleme Detayları:</h4>
                                <ul className="space-y-2 list-disc list-inside">
                                    <li><strong>İşlenen Veriler:</strong> IP adresi, konum bilgisi (izin verilirse), tarayıcı bilgisi, ziyaret edilen sayfalar</li>
                                    <li><strong>İşleme Amacı:</strong> Firma kimliklendirme, iş geliştirme fırsatları, istatistiksel analiz</li>
                                    <li><strong>Saklama Süresi:</strong> 2 yıl (yasal zorunluluklar hariç)</li>
                                    <li><strong>Üçüncü Taraflar:</strong> Google Geolocation API, IP veritabanı sağlayıcıları</li>
                                    <li><strong>Haklarınız:</strong> Verilerinize erişim, düzeltme, silme ve itiraz hakları KVKK kapsamında korunmaktadır</li>
                                </ul>
                                <p className="mt-3 text-xs text-[#64748b]">
                                    Detaylı bilgi için: <Link href="/privacy" className="text-[#00e5a0] hover:underline">Gizlilik Politikası</Link>
                                </p>
                            </div>
                        )}

                        {/* Actions */}
                        <div className="flex flex-col sm:flex-row gap-3">
                            <button
                                onClick={handleAccept}
                                className="flex-1 px-6 py-3 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-sm font-semibold cursor-pointer hover:opacity-90 transition-opacity"
                            >
                                ✓ Kabul Ediyorum
                            </button>
                            <button
                                onClick={() => setShowDetails(!showDetails)}
                                className="px-6 py-3 bg-transparent border border-[#1e3a5f] rounded-xl text-[#94a3b8] text-sm font-medium cursor-pointer hover:bg-[#0d1f35] transition-colors"
                            >
                                {showDetails ? '▲ Detayları Gizle' : '▼ Detayları Göster'}
                            </button>
                            <button
                                onClick={handleReject}
                                className="px-6 py-3 bg-transparent border border-[#ef444444] rounded-xl text-[#ef4444] text-sm font-medium cursor-pointer hover:bg-[#ef444411] transition-colors"
                            >
                                ✗ Reddet
                            </button>
                        </div>

                        {/* Footer Note */}
                        <p className="text-xs text-[#64748b] mt-4 text-center">
                            Bu siteyi kullanmaya devam ederek, veri işleme politikamızı kabul etmiş sayılırsınız.
                        </p>
                    </div>
                </div>
            </div>
        </>
    );
}
