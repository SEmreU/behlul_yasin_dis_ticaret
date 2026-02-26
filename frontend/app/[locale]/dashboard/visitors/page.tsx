'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import ExcelExportButton from '@/components/ExcelExportButton';
import GDPRBanner from '@/components/GDPRBanner';
import { exportVisitorsToExcel, isAuthorityEmail } from '@/lib/api-helpers';

interface Visitor {
    id: number;
    company: string;
    country: string;
    city: string;
    ip: string;
    created_at: string;
    confidence_score: number;
    email?: string;
}

export default function VisitorsPage() {
    const [visitors, setVisitors] = useState<Visitor[]>([]);
    const [loading, setLoading] = useState(true);
    const [excelLoading, setExcelLoading] = useState(false);

    useEffect(() => {
        fetchVisitors();
    }, []);

    const fetchVisitors = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/visitor/visitors?limit=100', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setVisitors(data);
            }
        } catch (error) {
            console.error('Ziyaretçi verisi alınamadı:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleExportExcel = async () => {
        setExcelLoading(true);
        try {
            await exportVisitorsToExcel(1000);
            alert('Excel dosyası başarıyla indirildi!');
        } catch (err) {
            console.error('Export error:', err);
            alert('Excel indirme başarısız oldu.');
        } finally {
            setExcelLoading(false);
        }
    };

    const getStatusBadge = (score: number) => {
        if (score >= 0.8) {
            return { text: '✓ Tespit Edildi', className: 'bg-[#00e5a022] text-[#00e5a0]' };
        } else if (score >= 0.5) {
            return { text: '⚡ IP Tespiti', className: 'bg-[#f59e0b22] text-[#f59e0b]' };
        } else {
            return { text: '? Anonim', className: 'bg-[#ef444422] text-[#ef4444]' };
        }
    };

    const formatTime = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 60) return `${diffMins} dk önce`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)} saat önce`;
        return `${Math.floor(diffMins / 1440)} gün önce`;
    };

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7 flex justify-between items-start">
                    <div>
                        <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🔭 Ziyaretçi Takip Sistemi</h2>
                        <p className="text-[15px] text-[#64748b] mt-2">
                            Web sitenizi ziyaret eden yurt dışı firmaları gerçek zamanlı takip edin
                        </p>
                    </div>
                    <ExcelExportButton
                        onClick={handleExportExcel}
                        loading={excelLoading}
                    />
                </div>

                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong>Nasıl Çalışır?</strong> Ziyaretçiye konum izni sorulur. &quot;Evet&quot; derse konum + firma eşleştirmesi yapılır (Google Geolocation API).
                    &quot;Hayır&quot; derse IP adresi üzerinden ülke ve firma tespiti yapılır. Tüm veriler otomatik bildirim olarak iletilir.
                </div>

                {/* Table Container */}
                <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl overflow-hidden">
                    {loading ? (
                        <div className="p-12 text-center text-[#64748b]">
                            <div className="animate-spin h-8 w-8 border-2 border-[#00e5a0] border-t-transparent rounded-full mx-auto mb-3"></div>
                            Ziyaretçiler yükleniyor...
                        </div>
                    ) : (
                        <table className="w-full border-collapse">
                            <thead>
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                        Firma
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                        Ülke
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                        Şehir
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                        IP Adresi
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                        Email
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                        Zaman
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider border-b border-[#1e3a5f44] bg-[#0a162888]">
                                        Durum
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {visitors.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} className="px-4 py-8 text-center text-[#64748b]">
                                            Henüz ziyaretçi kaydı yok
                                        </td>
                                    </tr>
                                ) : (
                                    visitors.map((v) => {
                                        const status = getStatusBadge(v.confidence_score);
                                        const isAuthority = v.email && isAuthorityEmail(v.email);

                                        return (
                                            <tr
                                                key={v.id}
                                                className={`border-b border-[#1e3a5f22] last:border-0 ${isAuthority ? 'bg-[#00e5a008]' : ''}`}
                                            >
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                    <strong>{v.company || 'Bilinmiyor'}</strong>
                                                </td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">{v.country || 'N/A'}</td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">{v.city || 'N/A'}</td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1] font-mono text-[13px]">{v.ip}</td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                    {v.email ? (
                                                        <span className="flex items-center gap-1">
                                                            {isAuthority && <span title="Yetkili Mail">📧</span>}
                                                            {v.email}
                                                        </span>
                                                    ) : (
                                                        <span className="text-[#64748b]">-</span>
                                                    )}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">{formatTime(v.created_at)}</td>
                                                <td className="px-4 py-3 text-sm text-[#cbd5e1]">
                                                    <span className={`px-2.5 py-1 rounded-md text-xs font-medium ${status.className}`}>
                                                        {status.text}
                                                    </span>
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {/* GDPR Banner */}
            <GDPRBanner />
        </DashboardLayout>
    );
}
