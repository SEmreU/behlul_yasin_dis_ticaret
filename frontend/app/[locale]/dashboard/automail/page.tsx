'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';

interface MailSendResult {
    sent: number;
    failed: number;
    provider: string;
    message: string;
    failed_addresses: string[];
}

export default function AutoMailPage() {
    const [senderName, setSenderName] = useState('');
    const [senderEmail, setSenderEmail] = useState('');
    const [subject, setSubject] = useState('');
    const [body, setBody] = useState('');
    const [recipientsText, setRecipientsText] = useState('');  // virgül/satır ile ayrılmış email listesi
    const [isHtml, setIsHtml] = useState(false);
    const [preview, setPreview] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<MailSendResult | null>(null);
    const [error, setError] = useState('');

    const parseRecipients = () =>
        recipientsText
            .split(/[\n,;]+/)
            .map(e => e.trim())
            .filter(e => e.includes('@'));

    const handleSend = async () => {
        const recipients = parseRecipients();
        if (!recipients.length) { setError('En az bir geçerli e-posta adresi girin'); return; }
        if (!subject.trim()) { setError('Konu boş olamaz'); return; }
        if (!body.trim()) { setError('Mail içeriği boş olamaz'); return; }

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${API_URL}/api/v1/mail/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({
                    sender_name: senderName || 'TradeRadar',
                    sender_email: senderEmail || 'noreply@traderadar.com',
                    recipients,
                    subject,
                    body,
                    is_html: isHtml,
                }),
            });

            const data = await res.json();
            if (res.ok) {
                setResult(data);
            } else {
                setError(data.detail || 'Gönderim başarısız');
            }
        } catch {
            setError('Sunucuya bağlanılamadı');
        } finally {
            setLoading(false);
        }
    };

    const recipientCount = parseRecipients().length;

    return (
        <DashboardLayout>
            <div className="p-8 max-w-3xl">
                {/* Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">📧 Otomatik Mail Gönderimi</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Toplu e-posta gönderimi — SendGrid › SMTP › Mock (key yoksa konsola yazar)
                    </p>
                </div>

                {/* Provider info */}
                <div className="bg-[#00e5a008] border border-[#00e5a022] rounded-xl p-4 mb-6 text-sm text-[#94a3b8] leading-7">
                    <strong className="text-[#00e5a0]">Mail Sağlayıcı Önceliği:</strong>{' '}
                    SendGrid (SENDGRID_API_KEY) → SMTP (SMTP_HOST) → Resend → Mock.
                    Hiç key yoksa test modunda çalışır, gerçek mail gitmez, konsola log yazar.
                    Ayarlar sayfasından key girebilirsiniz.
                </div>

                {/* Form */}
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Gönderici Adı</label>
                            <input
                                className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                placeholder="Örn: Yasin Dış Ticaret"
                                value={senderName}
                                onChange={e => setSenderName(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Gönderici E-posta</label>
                            <input
                                type="email"
                                className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                                placeholder="info@firmaniz.com"
                                value={senderEmail}
                                onChange={e => setSenderEmail(e.target.value)}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Konu</label>
                        <input
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors"
                            placeholder="Örn: Ürün Teklifimiz — Hydraulic Cylinder"
                            value={subject}
                            onChange={e => setSubject(e.target.value)}
                        />
                    </div>

                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="text-[13px] font-medium text-[#94a3b8]">Mail İçeriği</label>
                            <label className="flex items-center gap-2 text-xs text-[#94a3b8] cursor-pointer">
                                <input type="checkbox" checked={isHtml} onChange={e => setIsHtml(e.target.checked)}
                                    className="accent-[#00e5a0]" />
                                HTML modu
                            </label>
                        </div>
                        <textarea
                            rows={8}
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors resize-none font-mono"
                            placeholder={isHtml ? '<h1>Merhaba!</h1>\n<p>Ürünlerimizi incelemenizi öneririz...</p>' : 'Merhaba,\n\nÜrünlerimizi incelemenizi öneririz...'}
                            value={body}
                            onChange={e => setBody(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">
                            Alıcı Listesi{' '}
                            <span className="text-[#00e5a0]">({recipientCount} geçerli adres)</span>
                        </label>
                        <textarea
                            rows={4}
                            className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none focus:border-[#00e5a0] transition-colors resize-none font-mono"
                            placeholder={"ornek@firma.com\nalıcı2@mail.com, alıcı3@mail.com\n(virgül, noktalı virgül veya satır ile ayırın)"}
                            value={recipientsText}
                            onChange={e => setRecipientsText(e.target.value)}
                        />
                    </div>
                </div>

                {/* HTML Preview */}
                {preview && isHtml && body && (
                    <div className="mt-4 border border-[#1e3a5f] rounded-xl overflow-hidden">
                        <div className="px-4 py-2 bg-[#0d1f35] text-xs text-[#64748b] border-b border-[#1e3a5f]">
                            👁 HTML Önizleme
                        </div>
                        <div className="p-4 bg-white text-black text-sm"
                            dangerouslySetInnerHTML={{ __html: body }} />
                    </div>
                )}

                {error && (
                    <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                        ⚠️ {error}
                    </div>
                )}

                {result && (
                    <div className={`mt-4 p-4 rounded-xl border text-sm ${result.provider === 'mock'
                            ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300'
                            : 'bg-[#00e5a011] border-[#00e5a033] text-[#00e5a0]'
                        }`}>
                        <div className="font-semibold mb-1">
                            {result.provider === 'mock' ? '🧪 Test Modu' : '✅ Gönderildi'}
                        </div>
                        <div>{result.message}</div>
                        {result.failed > 0 && (
                            <div className="mt-2 text-red-400 text-xs">
                                Başarısız: {result.failed_addresses.join(', ')}
                            </div>
                        )}
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 mt-6">
                    {isHtml && (
                        <button
                            onClick={() => setPreview(p => !p)}
                            className="px-6 py-3 bg-[#0d1f35] border border-[#1e3a5f] rounded-xl text-[#94a3b8] text-sm font-medium hover:border-[#00e5a0] hover:text-[#00e5a0] transition-colors"
                        >
                            {preview ? '🙈 Önizlemeyi Gizle' : '👁 HTML Önizle'}
                        </button>
                    )}
                    <button
                        onClick={handleSend}
                        disabled={loading}
                        className="px-8 py-3.5 bg-gradient-to-br from-[#00e5a0] to-[#00b87a] border-none rounded-xl text-[#0a1628] text-[15px] font-semibold cursor-pointer disabled:opacity-50 transition-opacity"
                    >
                        {loading
                            ? `⏳ Gönderiliyor... (${recipientCount} alıcı)`
                            : `📤 ${recipientCount > 0 ? `${recipientCount} Kişiye ` : ''}Mail Gönder`
                        }
                    </button>
                </div>
            </div>
        </DashboardLayout>
    );
}
