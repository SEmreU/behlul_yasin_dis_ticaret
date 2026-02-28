'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import api from '@/lib/api';

const uuidv4 = () => crypto.randomUUID();

// ── Tema ──────────────────────────────────────────────────────────────────────
const C = {
    bg: '#060b18', bg2: '#0c1424', bg3: '#111c32', bg4: '#1a2844',
    gold: '#c9a227', goldL: '#e8c84a', goldD: 'rgba(201,162,39,0.12)', goldG: 'rgba(201,162,39,0.25)',
    cyan: '#22d3ee', green: '#34d399', violet: '#a78bfa', red: '#f87171',
    t1: '#f1f5f9', t2: '#94a3b8', t3: '#475569',
    bd: 'rgba(255,255,255,0.06)', bdA: 'rgba(201,162,39,0.2)',
};

// ── Types ────────────────────────────────────────────────────────────────────
interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface BotConfig {
    bot_name: string;
    welcome_message: string;
    supported_languages: string[];
    goal: string;
    company_info: Record<string, string> | null;
}

interface HistoryItem {
    session_id: string;
    message_count: number;
    first_message: string;
    collected_data: Record<string, string>;
    is_completed: boolean;
    language: string;
    created_at: string | null;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmtTime(d: Date) {
    return d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}
function fmtDate(s: string | null) {
    if (!s) return '';
    return new Date(s).toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit', year: '2-digit' });
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function ChatbotPage() {
    const [activeTab, setActiveTab] = useState<'chat' | 'history' | 'settings'>('chat');
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId] = useState(uuidv4);
    const [config, setConfig] = useState<BotConfig>({
        bot_name: 'TradeBot', welcome_message: 'Merhaba! Size nasıl yardımcı olabilirim?',
        supported_languages: ['tr', 'en', 'de'], goal: 'email', company_info: null,
    });
    const [configSaving, setConfigSaving] = useState(false);
    const [embedCode, setEmbedCode] = useState('');
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [selectedConv, setSelectedConv] = useState<{ messages: Message[]; item: HistoryItem } | null>(null);
    const [sessionStats, setSessionStats] = useState({ totalConversations: 0, leadsCollected: 0, activeChats: 0 });
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // ── Init ─────────────────────────────────────────────────────────────────
    useEffect(() => {
        setMessages([{ id: uuidv4(), role: 'assistant', content: config.welcome_message, timestamp: new Date() }]);
        api.get('/api/v1/chatbot/stats').then(r => {
            setSessionStats({
                totalConversations: r.data.total_conversations,
                leadsCollected: r.data.leads_collected,
                activeChats: r.data.active_chats,
            });
        }).catch(() => { });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

    // ── History ───────────────────────────────────────────────────────────────
    const fetchHistory = useCallback(async () => {
        setHistoryLoading(true);
        try {
            const r = await api.get('/api/v1/chatbot/history?limit=40');
            setHistory(r.data.conversations || []);
        } catch { }
        setHistoryLoading(false);
    }, []);

    useEffect(() => { if (activeTab === 'history') fetchHistory(); }, [activeTab, fetchHistory]);

    const loadConv = async (item: HistoryItem) => {
        try {
            const r = await api.get(`/api/v1/chatbot/history/${item.session_id}`);
            const msgs: Message[] = (r.data.messages || []).map((m: { role: string; content: string; timestamp: string }) => ({
                id: uuidv4(), role: m.role as 'user' | 'assistant',
                content: m.content, timestamp: new Date(m.timestamp),
            }));
            setSelectedConv({ messages: msgs, item });
        } catch { alert('Konuşma yüklenemedi'); }
    };

    // ── Send message ─────────────────────────────────────────────────────────
    const sendMessage = async (text: string) => {
        if (!text.trim() || isLoading) return;
        const userMsg: Message = { id: uuidv4(), role: 'user', content: text, timestamp: new Date() };
        setMessages(p => [...p, userMsg]);
        setInputText('');
        setIsLoading(true);
        try {
            const r = await api.post('/api/v1/chatbot/chat', { session_id: sessionId, message: text, language: 'tr' });
            setMessages(p => [...p, { id: uuidv4(), role: 'assistant', content: r.data.reply, timestamp: new Date() }]);
        } catch {
            setMessages(p => [...p, { id: uuidv4(), role: 'assistant', content: '⚠️ Sunucuya bağlanılamadı.', timestamp: new Date() }]);
        } finally {
            setIsLoading(false);
            setTimeout(() => inputRef.current?.focus(), 80);
        }
    };

    const saveConfig = async () => {
        setConfigSaving(true);
        try {
            const r = await api.post('/api/v1/chatbot/config', config);
            setEmbedCode(r.data.embed_code || '');
        } catch { alert('Kayıt başarısız'); }
        setConfigSaving(false);
    };

    // ── Quick prompts ─────────────────────────────────────────────────────────
    const QUICK = ['Merhaba, bilgi almak istiyorum', 'Fiyat listesi var mı?', 'Ürün kataloğunuzu görebilir miyim?'];

    return (
        <DashboardLayout>
            <style>{`
                .cb-tab{display:flex;align-items:center;gap:8px;padding:9px 18px;border-radius:10px;font-size:13px;font-weight:500;cursor:pointer;border:none;transition:all .2s;font-family:inherit}
                .cb-tab-active{background:${C.goldD};color:${C.gold};border:1px solid ${C.bdA};}
                .cb-tab-idle{background:transparent;color:${C.t3};border:1px solid transparent;}
                .cb-tab-idle:hover{background:${C.bg4};color:${C.t2};}
                .cb-input{background:${C.bg3};border:1px solid ${C.bd};border-radius:12px;padding:11px 16px;color:${C.t1};font-size:14px;font-family:inherit;outline:none;transition:border .2s;width:100%}
                .cb-input:focus{border-color:${C.gold}66}
                .cb-btn-gold{background:linear-gradient(135deg,${C.gold},${C.goldL});color:${C.bg};border:none;border-radius:10px;padding:10px 20px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit;transition:opacity .2s}
                .cb-btn-gold:disabled{opacity:.5;cursor:not-allowed}
                .cb-btn-ghost{background:${C.bg4};color:${C.t2};border:1px solid ${C.bd};border-radius:10px;padding:9px 16px;font-size:13px;font-weight:500;cursor:pointer;font-family:inherit;transition:all .2s}
                .cb-btn-ghost:hover{border-color:${C.bdA};color:${C.gold}}
                .cb-card{background:${C.bg2};border:1px solid ${C.bd};border-radius:16px}
                .cb-history-row{width:100%;text-align:left;background:transparent;border:none;border-bottom:1px solid ${C.bd};padding:12px 20px;cursor:pointer;transition:background .15s;font-family:inherit}
                .cb-history-row:hover{background:${C.bg4}}
                .cb-history-row.active{background:${C.goldD};border-left:3px solid ${C.gold}}
                .cb-scroll::-webkit-scrollbar{width:4px}.cb-scroll::-webkit-scrollbar-track{background:transparent}.cb-scroll::-webkit-scrollbar-thumb{background:${C.bg4};border-radius:2px}
                .cb-bubble-user{background:linear-gradient(135deg,${C.gold},${C.goldL});color:${C.bg};border-radius:18px 18px 4px 18px;}
                .cb-bubble-bot{background:${C.bg4};color:${C.t1};border:1px solid ${C.bd};border-radius:18px 18px 18px 4px;}
                .cb-typing span{display:inline-block;width:7px;height:7px;background:${C.gold};border-radius:50%;margin:0 2px;animation:cb-bounce .8s infinite}.cb-typing span:nth-child(2){animation-delay:.15s}.cb-typing span:nth-child(3){animation-delay:.3s}
                @keyframes cb-bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
                .cb-stat-card{background:${C.bg3};border:1px solid ${C.bd};border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:4px}
                .cb-send-btn{width:44px;height:44px;flex-shrink:0;background:linear-gradient(135deg,${C.gold},${C.goldL});border:none;border-radius:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:opacity .2s}
                .cb-send-btn:disabled{opacity:.4;cursor:not-allowed}
                .cb-quick-btn{background:${C.bg4};border:1px solid ${C.bd};border-radius:20px;padding:7px 14px;color:${C.t2};font-size:12px;cursor:pointer;font-family:inherit;transition:all .2s;white-space:nowrap}
                .cb-quick-btn:hover{border-color:${C.bdA};color:${C.gold}}
            `}</style>

            <div style={{ padding: '28px', maxWidth: 1280, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 24 }}>

                {/* ── PAGE HEADER ── */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <div style={{ width: 44, height: 44, borderRadius: 12, background: `linear-gradient(135deg,${C.gold},${C.goldL})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, boxShadow: `0 0 20px ${C.goldG}` }}>🤖</div>
                            <div>
                                <h1 style={{ fontSize: 22, fontWeight: 700, color: C.t1, fontFamily: "'Plus Jakarta Sans',sans-serif" }}>AI Chatbot</h1>
                                <p style={{ fontSize: 13, color: C.t3, marginTop: 2 }}>Akıllı satış asistanı — Groq Llama 3.1 destekli</p>
                            </div>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div style={{ display: 'flex', gap: 8 }}>
                        {(['chat', 'history', 'settings'] as const).map(tab => (
                            <button key={tab} className={`cb-tab ${activeTab === tab ? 'cb-tab-active' : 'cb-tab-idle'}`} onClick={() => setActiveTab(tab)}>
                                {tab === 'chat' ? '💬 Sohbet' : tab === 'history' ? '📋 Geçmiş' : '⚙️ Ayarlar'}
                            </button>
                        ))}
                    </div>
                </div>

                {/* ── STATS ROW ── */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 14 }}>
                    {[
                        { label: 'Toplam Sohbet', value: sessionStats.totalConversations, color: C.cyan, icon: '💬' },
                        { label: 'Lead Toplandı', value: sessionStats.leadsCollected, color: C.green, icon: '📩' },
                        { label: 'Aktif Sohbet', value: sessionStats.activeChats, color: C.gold, icon: '🟢' },
                        { label: 'AI Sağlayıcı', value: 'Groq', color: C.violet, icon: '⚡' },
                    ].map(s => (
                        <div key={s.label} className="cb-stat-card">
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ fontSize: 18 }}>{s.icon}</span>
                                <span style={{ fontSize: 12, color: C.t3 }}>{s.label}</span>
                            </div>
                            <div style={{ fontSize: 26, fontWeight: 700, color: s.color }}>{s.value}</div>
                        </div>
                    ))}
                </div>

                {/* ══════════════════════════════════════════════════════════════════════
                    TAB: CHAT
                ══════════════════════════════════════════════════════════════════════ */}
                {activeTab === 'chat' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 20 }}>
                        {/* Chat window */}
                        <div className="cb-card" style={{ display: 'flex', flexDirection: 'column', height: 580 }}>
                            {/* Chat header */}
                            <div style={{ padding: '14px 20px', borderBottom: `1px solid ${C.bd}`, display: 'flex', alignItems: 'center', gap: 14 }}>
                                <div style={{ position: 'relative' }}>
                                    <div style={{ width: 40, height: 40, borderRadius: 12, background: `linear-gradient(135deg,${C.gold},${C.goldL})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>🤖</div>
                                    <div style={{ position: 'absolute', bottom: 0, right: 0, width: 11, height: 11, background: C.green, borderRadius: '50%', border: `2px solid ${C.bg2}` }} />
                                </div>
                                <div>
                                    <div style={{ fontWeight: 600, color: C.t1, fontSize: 14 }}>{config.bot_name}</div>
                                    <div style={{ fontSize: 12, color: C.green }}>● Çevrimiçi</div>
                                </div>
                                <div style={{ marginLeft: 'auto', fontSize: 11, color: C.t3, fontFamily: 'monospace' }}>
                                    {sessionId.slice(0, 8)}…
                                </div>
                            </div>

                            {/* Messages */}
                            <div className="cb-scroll" style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: 14 }}>
                                {messages.map(msg => (
                                    <div key={msg.id} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                                        {msg.role === 'assistant' && (
                                            <div style={{ width: 28, height: 28, borderRadius: 8, background: `linear-gradient(135deg,${C.gold},${C.goldL})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, flexShrink: 0, marginRight: 8, marginTop: 4 }}>🤖</div>
                                        )}
                                        <div style={{ maxWidth: '68%' }}>
                                            <div className={msg.role === 'user' ? 'cb-bubble-user' : 'cb-bubble-bot'} style={{ padding: '10px 14px', fontSize: 14, lineHeight: 1.6 }}>
                                                {msg.content}
                                            </div>
                                            <div style={{ fontSize: 11, color: C.t3, marginTop: 4, textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                                                {fmtTime(msg.timestamp)}
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                {isLoading && (
                                    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 10 }}>
                                        <div style={{ width: 28, height: 28, borderRadius: 8, background: `linear-gradient(135deg,${C.gold},${C.goldL})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14 }}>🤖</div>
                                        <div className="cb-bubble-bot" style={{ padding: '12px 16px' }}>
                                            <div className="cb-typing"><span /><span /><span /></div>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Quick prompts */}
                            <div style={{ padding: '10px 16px 0', display: 'flex', gap: 8, overflowX: 'auto' }}>
                                {QUICK.map(q => (
                                    <button key={q} className="cb-quick-btn" onClick={() => sendMessage(q)} disabled={isLoading}>{q}</button>
                                ))}
                            </div>

                            {/* Input area */}
                            <div style={{ padding: '14px 16px', borderTop: `1px solid ${C.bd}`, display: 'flex', gap: 10, alignItems: 'center' }}>
                                <input
                                    ref={inputRef}
                                    className="cb-input"
                                    value={inputText}
                                    onChange={e => setInputText(e.target.value)}
                                    onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(inputText); } }}
                                    placeholder="Mesajınızı yazın…"
                                    disabled={isLoading}
                                    style={{ flex: 1 }}
                                />
                                <button className="cb-send-btn" onClick={() => sendMessage(inputText)} disabled={!inputText.trim() || isLoading}>
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={C.bg} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="m22 2-11 11" /><path d="m22 2-7 20-4-9-9-4 20-7z" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        {/* Right panel */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                            {/* Session info */}
                            <div className="cb-card" style={{ padding: 20 }}>
                                <div style={{ fontSize: 13, fontWeight: 600, color: C.gold, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <span>📊</span> Oturum Bilgisi
                                </div>
                                {[
                                    { label: 'Mesaj Sayısı', value: messages.length, color: C.t1 },
                                    { label: 'Hedef', value: config.goal === 'email' ? 'E-mail' : config.goal === 'phone' ? 'Telefon' : 'İkisi de', color: C.cyan },
                                    { label: 'Model', value: 'Llama 3.1', color: C.violet },
                                ].map(r => (
                                    <div key={r.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: `1px solid ${C.bd}` }}>
                                        <span style={{ fontSize: 12, color: C.t3 }}>{r.label}</span>
                                        <span style={{ fontSize: 12, fontWeight: 600, color: r.color }}>{r.value}</span>
                                    </div>
                                ))}
                            </div>

                            {/* Embed code shortcut */}
                            <div className="cb-card" style={{ padding: 20 }}>
                                <div style={{ fontSize: 13, fontWeight: 600, color: C.gold, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <span>🔗</span> Web Entegrasyonu
                                </div>
                                <p style={{ fontSize: 12, color: C.t3, lineHeight: 1.6, marginBottom: 12 }}>
                                    Bu botu web sitenize eklemek için Ayarlar&#39;dan embed kodu oluşturun.
                                </p>
                                <button className="cb-btn-ghost" style={{ width: '100%' }} onClick={() => setActiveTab('settings')}>
                                    ⚙️ Ayarlara Git
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* ══════════════════════════════════════════════════════════════════════
                    TAB: HISTORY
                ══════════════════════════════════════════════════════════════════════ */}
                {activeTab === 'history' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20 }}>
                        {/* Conversation list */}
                        <div className="cb-card" style={{ display: 'flex', flexDirection: 'column', height: 600, overflow: 'hidden' }}>
                            <div style={{ padding: '14px 20px', borderBottom: `1px solid ${C.bd}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <span style={{ fontSize: 13, fontWeight: 600, color: C.t1 }}>Geçmiş Sohbetler</span>
                                <button className="cb-btn-ghost" style={{ padding: '5px 12px', fontSize: 12 }} onClick={fetchHistory}>🔄 Yenile</button>
                            </div>
                            <div className="cb-scroll" style={{ flex: 1, overflowY: 'auto' }}>
                                {historyLoading && (
                                    <div style={{ padding: 40, textAlign: 'center', color: C.t3, fontSize: 13 }}>
                                        <div className="cb-typing" style={{ justifyContent: 'center', display: 'flex', marginBottom: 8 }}><span /><span /><span /></div>
                                        Yükleniyor…
                                    </div>
                                )}
                                {!historyLoading && history.length === 0 && (
                                    <div style={{ padding: 40, textAlign: 'center', color: C.t3, fontSize: 13 }}>
                                        <div style={{ fontSize: 32, marginBottom: 8 }}>💬</div>
                                        Henüz sohbet geçmişi yok
                                    </div>
                                )}
                                {history.map(item => (
                                    <button key={item.session_id}
                                        className={`cb-history-row ${selectedConv?.item.session_id === item.session_id ? 'active' : ''}`}
                                        onClick={() => loadConv(item)}
                                    >
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                                            <div style={{ flex: 1, minWidth: 0 }}>
                                                <div style={{ fontSize: 13, color: C.t1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                    {item.first_message || '(boş)'}
                                                </div>
                                                <div style={{ display: 'flex', gap: 8, marginTop: 4, flexWrap: 'wrap' }}>
                                                    <span style={{ fontSize: 11, color: C.t3 }}>{item.message_count} mesaj</span>
                                                    {item.collected_data?.email && <span style={{ fontSize: 11, color: C.green }}>✉ {item.collected_data.email}</span>}
                                                    {item.collected_data?.phone && <span style={{ fontSize: 11, color: C.cyan }}>📞 {item.collected_data.phone}</span>}
                                                </div>
                                            </div>
                                            <div style={{ textAlign: 'right', flexShrink: 0 }}>
                                                {item.is_completed && <div style={{ fontSize: 10, background: `${C.green}22`, color: C.green, padding: '2px 6px', borderRadius: 4, marginBottom: 4 }}>✓ Tamamlandı</div>}
                                                <div style={{ fontSize: 11, color: C.t3 }}>{fmtDate(item.created_at)}</div>
                                            </div>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Conversation detail */}
                        <div className="cb-card" style={{ display: 'flex', flexDirection: 'column', height: 600, overflow: 'hidden' }}>
                            {!selectedConv ? (
                                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: C.t3, gap: 12 }}>
                                    <div style={{ fontSize: 48 }}>📋</div>
                                    <p style={{ fontSize: 14 }}>Sol panelden bir sohbet seçin</p>
                                </div>
                            ) : (
                                <>
                                    {/* Detail header */}
                                    <div style={{ padding: '14px 20px', borderBottom: `1px solid ${C.bd}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <div>
                                            <div style={{ fontSize: 13, fontWeight: 600, color: C.t1 }}>Sohbet Detayı</div>
                                            <div style={{ fontSize: 11, color: C.t3, fontFamily: 'monospace' }}>{selectedConv.item.session_id.slice(0, 20)}…</div>
                                        </div>
                                        <div style={{ display: 'flex', gap: 10, fontSize: 12 }}>
                                            {selectedConv.item.collected_data?.email && (
                                                <span style={{ background: `${C.green}22`, color: C.green, padding: '4px 10px', borderRadius: 6 }}>✉ {selectedConv.item.collected_data.email}</span>
                                            )}
                                            {selectedConv.item.collected_data?.phone && (
                                                <span style={{ background: `${C.cyan}22`, color: C.cyan, padding: '4px 10px', borderRadius: 6 }}>📞 {selectedConv.item.collected_data.phone}</span>
                                            )}
                                        </div>
                                    </div>
                                    {/* Messages */}
                                    <div className="cb-scroll" style={{ flex: 1, overflowY: 'auto', padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
                                        {selectedConv.messages.map(msg => (
                                            <div key={msg.id} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                                                {msg.role === 'assistant' && (
                                                    <div style={{ width: 26, height: 26, borderRadius: 8, background: `linear-gradient(135deg,${C.gold},${C.goldL})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, flexShrink: 0, marginRight: 8, marginTop: 2 }}>🤖</div>
                                                )}
                                                <div>
                                                    <div className={msg.role === 'user' ? 'cb-bubble-user' : 'cb-bubble-bot'} style={{ padding: '9px 13px', fontSize: 13, lineHeight: 1.6, maxWidth: 400 }}>
                                                        {msg.content}
                                                    </div>
                                                    <div style={{ fontSize: 10, color: C.t3, marginTop: 3, textAlign: msg.role === 'user' ? 'right' : 'left' }}>{fmtTime(msg.timestamp)}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                )}

                {/* ══════════════════════════════════════════════════════════════════════
                    TAB: SETTINGS
                ══════════════════════════════════════════════════════════════════════ */}
                {activeTab === 'settings' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                        {/* Config form */}
                        <div className="cb-card" style={{ padding: 28 }}>
                            <h2 style={{ fontSize: 16, fontWeight: 600, color: C.t1, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{ color: C.gold }}>⚙️</span> Bot Yapılandırması
                            </h2>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
                                <div>
                                    <label style={{ fontSize: 12, color: C.t3, display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 }}>Bot Adı</label>
                                    <input className="cb-input" value={config.bot_name} onChange={e => setConfig(p => ({ ...p, bot_name: e.target.value }))} />
                                </div>
                                <div>
                                    <label style={{ fontSize: 12, color: C.t3, display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 }}>Lead Hedefi</label>
                                    <select className="cb-input" value={config.goal} onChange={e => setConfig(p => ({ ...p, goal: e.target.value }))} style={{ cursor: 'pointer' }}>
                                        <option value="email">📧 Sadece E-mail</option>
                                        <option value="phone">📞 Sadece Telefon</option>
                                        <option value="both">📧📞 E-mail ve Telefon</option>
                                    </select>
                                </div>
                                <div>
                                    <label style={{ fontSize: 12, color: C.t3, display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 }}>Karşılama Mesajı</label>
                                    <textarea
                                        className="cb-input"
                                        value={config.welcome_message}
                                        onChange={e => setConfig(p => ({ ...p, welcome_message: e.target.value }))}
                                        rows={3}
                                        style={{ resize: 'none', lineHeight: 1.6 }}
                                    />
                                </div>
                                <div>
                                    <label style={{ fontSize: 12, color: C.t3, display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 }}>Şirket Adı</label>
                                    <input
                                        className="cb-input"
                                        value={config.company_info?.name || ''}
                                        onChange={e => setConfig(p => ({ ...p, company_info: { ...(p.company_info || {}), name: e.target.value } }))}
                                        placeholder="Yasin Dış Ticaret"
                                    />
                                </div>

                                <div style={{ display: 'flex', gap: 10, paddingTop: 4 }}>
                                    <button className="cb-btn-gold" onClick={saveConfig} disabled={configSaving} style={{ flex: 1 }}>
                                        {configSaving ? 'Kaydediliyor…' : '💾 Ayarları Kaydet'}
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Embed code + info */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                            <div className="cb-card" style={{ padding: 24 }}>
                                <h3 style={{ fontSize: 14, fontWeight: 600, color: C.gold, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    🔗 Web Sitesi Entegrasyonu
                                </h3>
                                {embedCode ? (
                                    <>
                                        <p style={{ fontSize: 12, color: C.t3, marginBottom: 10 }}>Aşağıdaki kodu web sitenize ekleyin:</p>
                                        <div style={{ background: C.bg, border: `1px solid ${C.bd}`, borderRadius: 10, padding: 14, position: 'relative' }}>
                                            <code style={{ fontSize: 11, color: C.green, fontFamily: 'monospace', wordBreak: 'break-all', lineHeight: 1.6 }}>{embedCode}</code>
                                        </div>
                                        <button className="cb-btn-ghost" style={{ marginTop: 10, width: '100%', fontSize: 12 }} onClick={() => navigator.clipboard.writeText(embedCode)}>
                                            📋 Kodu Kopyala
                                        </button>
                                    </>
                                ) : (
                                    <p style={{ fontSize: 13, color: C.t3, lineHeight: 1.7 }}>
                                        Ayarları kaydettikten sonra embed kodu burada görüntülenir.
                                        Web sitenizin herhangi bir sayfasına ekleyerek botu aktif hale getirebilirsiniz.
                                    </p>
                                )}
                            </div>

                            <div className="cb-card" style={{ padding: 24 }}>
                                <h3 style={{ fontSize: 14, fontWeight: 600, color: C.gold, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
                                    ⚡ AI Sağlayıcı Durumu
                                </h3>
                                {[
                                    { name: 'Groq Llama 3.1', status: 'Aktif', color: C.green, note: 'Birincil — ücretsiz' },
                                    { name: 'HuggingFace', status: 'Yedek', color: C.cyan, note: 'İkincil — ücretsiz' },
                                    { name: 'Pattern Fallback', status: 'Yedek', color: C.t3, note: 'Her zaman çalışır' },
                                ].map(p => (
                                    <div key={p.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: `1px solid ${C.bd}` }}>
                                        <div>
                                            <div style={{ fontSize: 13, color: C.t1 }}>{p.name}</div>
                                            <div style={{ fontSize: 11, color: C.t3 }}>{p.note}</div>
                                        </div>
                                        <span style={{ fontSize: 11, color: p.color, background: `${p.color}22`, padding: '3px 10px', borderRadius: 6 }}>{p.status}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
