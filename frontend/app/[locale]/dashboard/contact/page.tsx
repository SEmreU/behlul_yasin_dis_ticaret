'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import api from '@/lib/api';

interface ContactResult {
    url: string;
    emails: string[];
    phones: string[];
    social_media: Record<string, string>;
    error?: string;
}

const POSITIONS = ['Purchasing Manager', 'Sales Manager', 'General Manager', 'Owner/CEO', 'Import Manager'];

export default function ContactPage() {
    const [websites, setWebsites] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<ContactResult[] | null>(null);
    const [summary, setSummary] = useState<{ emails: number; phones: number } | null>(null);
    const [error, setError] = useState('');

    const handleFind = async () => {
        const urls = websites
            .split('\n')
            .map(u => u.trim())
            .filter(Boolean);

        if (urls.length === 0) {
            setError('Lütfen en az bir web sitesi girin');
            return;
        }

        setLoading(true);
        setError('');
        setResults(null);
        setSummary(null);

        try {
            const res = await api.post('/contact/find', {
                websites: urls,
            });
            setResults(res.data.results);
            setSummary({
                emails: res.data.total_emails_found,
                phones: res.data.total_phones_found,
            });
        } catch (e: unknown) {
            const err = e as { response?: { data?: { detail?: string } } };
            setError(err?.response?.data?.detail || 'Bağlantı hatası oluştu');
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="p-8">
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">📧 Yetkili İletişim Bulucu</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Web sitelerindeki info@ adresleri yerine gerçek yetkili e-posta adreslerini bulun
                    </p>
                </div>

                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong>Problem:</strong> Firmaların iletişim sayfalarında genellikle info@firma.com gibi genel adresler bulunur.
                    Bu modül, <strong>purchasing@</strong>, <strong>manager@</strong> veya kişisel yetkili e-posta adreslerini web sitesi verilerinden çıkarır.
                    {' '}<span className="text-[#00e5a0]">ScraperAPI key eklenirse başarı oranı artar.</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                    <div className="col-span-2 md:col-span-1">
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            Firma Web Siteleri (her satıra bir tane)
                        </label>
                        <textarea
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none resize-y focus:border-[#00e5a0] transition-colors"
                            rows={7}
                            placeholder={'www.firma1.com\nwww.firma2.de\nwww.firma3.co.uk'}
                            value={websites}
                            onChange={e => setWebsites(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            Aranan Pozisyon
                        </label>
                        <div className="space-y-2">
                            {POSITIONS.map((p) => (
                                <label key={p} className="flex items-center gap-1.5 text-sm text-[#cbd5e1] cursor-pointer">
                                    <input type="checkbox" defaultChecked className="accent-[#00e5a0]" />
                                    {p}
                                </label>
                            ))}
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                        ⚠️ {error}
                    </div>
                )}

                <button
                    onClick={handleFind}
                    disabled={loading}
                    className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer disabled:opacity-50 transition-opacity"
                >
                    {loading ? '⏳ Taranıyor...' : '🔍 Yetkili Bilgilerini Bul'}
                </button>

                {/* Results */}
                {summary && (
                    <div className="mt-8">
                        <div className="flex gap-4 mb-5">
                            <div className="bg-[#00e5a022] border border-[#00e5a044] rounded-xl px-5 py-3 text-center">
                                <div className="text-2xl font-bold text-[#00e5a0]">{summary.emails}</div>
                                <div className="text-xs text-[#64748b]">E-posta Bulundu</div>
                            </div>
                            <div className="bg-[#0ea5e922] border border-[#0ea5e944] rounded-xl px-5 py-3 text-center">
                                <div className="text-2xl font-bold text-[#0ea5e9]">{summary.phones}</div>
                                <div className="text-xs text-[#64748b]">Telefon Bulundu</div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {results?.map((r, i) => (
                                <div key={i} className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl p-5">
                                    <div className="flex items-center gap-2 mb-3">
                                        <span className="text-[#00e5a0] text-sm font-mono">{r.url}</span>
                                        {r.error && <span className="text-xs text-yellow-500">⚠️ {r.error}</span>}
                                    </div>

                                    {r.emails.length > 0 && (
                                        <div className="mb-2">
                                            <span className="text-xs text-[#64748b] uppercase tracking-wider">E-postalar</span>
                                            <div className="flex flex-wrap gap-2 mt-1">
                                                {r.emails.map((email, j) => (
                                                    <span key={j} className="px-2 py-1 bg-[#00e5a011] border border-[#00e5a033] rounded text-[#00e5a0] text-xs font-mono">
                                                        {email}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {r.phones.length > 0 && (
                                        <div className="mb-2">
                                            <span className="text-xs text-[#64748b] uppercase tracking-wider">Telefonlar</span>
                                            <div className="flex flex-wrap gap-2 mt-1">
                                                {r.phones.map((phone, j) => (
                                                    <span key={j} className="px-2 py-1 bg-[#0ea5e911] border border-[#0ea5e933] rounded text-[#0ea5e9] text-xs font-mono">
                                                        {phone}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {Object.keys(r.social_media || {}).length > 0 && (
                                        <div>
                                            <span className="text-xs text-[#64748b] uppercase tracking-wider">Sosyal Medya</span>
                                            <div className="flex flex-wrap gap-2 mt-1">
                                                {Object.entries(r.social_media).map(([platform, url]) => (
                                                    <a key={platform} href={url} target="_blank" rel="noopener noreferrer"
                                                        className="px-2 py-1 bg-[#8b5cf611] border border-[#8b5cf633] rounded text-[#8b5cf6] text-xs hover:underline">
                                                        {platform}
                                                    </a>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {r.emails.length === 0 && r.phones.length === 0 && !r.error && (
                                        <p className="text-sm text-[#64748b]">Bu sitede iletişim bilgisi bulunamadı</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
