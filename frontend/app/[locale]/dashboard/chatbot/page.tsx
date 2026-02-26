'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';

export default function ChatbotPage() {
    const [messages] = useState([
        { role: 'bot', text: 'Merhaba! Size nasıl yardımcı olabilirim? 👋' },
        { role: 'user', text: "I'm looking for piston suppliers from Turkey" },
        { role: 'bot', text: 'Great! We specialize in high-quality pistons for automotive engines. Could you share your email so I can send you our catalog and price list?' },
    ]);

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Page Header */}
                <div className="mb-7">
                    <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">🤖 AI Chatbot Modülü</h2>
                    <p className="text-[15px] text-[#64748b] mt-2">
                        Müşterilerinizin web sitesine yerleştirilebilir çok dilli AI sohbet robotu
                    </p>
                </div>

                {/* Chatbot Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6">
                    {/* Settings */}
                    <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl p-6">
                        <h4 className="text-base font-semibold text-[#e2e8f0] m-0 mb-5">Chatbot Ayarları</h4>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Bot Adı</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Örn: TradeAssistant"
                                />
                            </div>
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Karşılama Mesajı</label>
                                <input
                                    className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                    placeholder="Merhaba! Size nasıl yardımcı olabilirim?"
                                />
                            </div>
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Desteklenen Diller</label>
                                <div className="space-y-2">
                                    {['Türkçe', 'İngilizce', 'Almanca', 'Rusça', 'Arapça', 'Fransızca'].map((l) => (
                                        <label key={l} className="flex items-center gap-1.5 text-sm text-[#cbd5e1] cursor-pointer">
                                            <input type="checkbox" defaultChecked className="accent-[#00e5a0]" />
                                            {l}
                                        </label>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="block text-[13px] font-medium text-[#94a3b8] mb-2">Ana Hedef</label>
                                <select className="w-full px-3.5 py-3 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none">
                                    <option>📧 E-posta adresi toplama</option>
                                    <option>📞 Telefon numarası toplama</option>
                                    <option>📋 Her ikisi</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Chat Preview */}
                    <div className="bg-[#0d1f35] border border-[#1e3a5f] rounded-[20px] overflow-hidden flex flex-col h-[480px]">
                        <div className="px-4 py-3 bg-[#0a1628] border-b border-[#1e3a5f44] flex items-center gap-2.5 text-[15px] font-semibold text-[#e2e8f0]">
                            <div className="w-2 h-2 rounded-full bg-[#00e5a0]" />
                            <span>TradeAssistant</span>
                            <span className="text-xs opacity-60 ml-auto">Online</span>
                        </div>
                        <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-2.5">
                            {messages.map((m, i) => (
                                <div
                                    key={i}
                                    className={`px-3.5 py-2.5 rounded-[14px] text-sm max-w-[85%] ${m.role === 'bot'
                                            ? 'self-start bg-[#132744] text-[#cbd5e1] rounded-tl-[4px]'
                                            : 'self-end bg-gradient-to-br from-[#00e5a033] to-[#00b87a33] text-[#e2e8f0] rounded-tr-[4px]'
                                        }`}
                                >
                                    {m.text}
                                </div>
                            ))}
                        </div>
                        <div className="p-3 border-t border-[#1e3a5f44] flex gap-2">
                            <input
                                className="flex-1 px-3.5 py-2.5 bg-[#0a1628] border border-[#1e3a5f] rounded-lg text-[#e2e8f0] text-sm outline-none"
                                placeholder="Mesajınızı yazın..."
                            />
                            <button className="w-10 h-10 bg-[#00e5a0] border-none rounded-lg text-[#0a1628] text-lg flex items-center justify-center cursor-pointer">
                                ➤
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
