'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import api from '@/lib/api';
const uuidv4 = () => crypto.randomUUID();

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

export default function ChatbotPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId] = useState(() => uuidv4());
    const [config, setConfig] = useState<BotConfig>({
        bot_name: 'TradeBot',
        welcome_message: 'Merhaba! Size nasıl yardımcı olabilirim?',
        supported_languages: ['tr', 'en', 'de'],
        goal: 'email',
        company_info: null,
    });
    const [configMode, setConfigMode] = useState(false);
    const [configSaving, setConfigSaving] = useState(false);
    const [embedCode, setEmbedCode] = useState('');
    const [activeTab, setActiveTab] = useState<'chat' | 'history'>('chat');
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [selectedConv, setSelectedConv] = useState<{ messages: Message[]; session_id: string } | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        setMessages([{
            id: uuidv4(),
            role: 'assistant',
            content: config.welcome_message,
            timestamp: new Date(),
        }]);
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const fetchHistory = useCallback(async () => {
        setHistoryLoading(true);
        try {
            const res = await api.get('/api/v1/chatbot/history?limit=30');
            setHistory(res.data.conversations || []);
        } catch {
            // sessizce geç
        } finally {
            setHistoryLoading(false);
        }
    }, []);

    useEffect(() => {
        if (activeTab === 'history') fetchHistory();
    }, [activeTab, fetchHistory]);

    const loadConversation = async (sid: string) => {
        try {
            const res = await api.get(`/api/v1/chatbot/history/${sid}`);
            const msgs: Message[] = (res.data.messages || []).map((m: { role: string; content: string; timestamp: string }) => ({
                id: uuidv4(),
                role: m.role as 'user' | 'assistant',
                content: m.content,
                timestamp: new Date(m.timestamp),
            }));
            setSelectedConv({ messages: msgs, session_id: sid });
        } catch {
            alert('Konuşma yüklenemedi');
        }
    };

    const sendMessage = async (text: string) => {
        if (!text.trim() || isLoading) return;

        const userMsg: Message = {
            id: uuidv4(),
            role: 'user',
            content: text,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMsg]);
        setInputText('');
        setIsLoading(true);

        try {
            const res = await api.post('/api/v1/chatbot/chat', {
                session_id: sessionId,
                message: text,
                language: 'tr',
            });

            const botMsg: Message = {
                id: uuidv4(),
                role: 'assistant',
                content: res.data.reply,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, botMsg]);
        } catch {
            const errMsg: Message = {
                id: uuidv4(),
                role: 'assistant',
                content: '⚠️ Bağlantı hatası. Backend çalışıyor mu?',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errMsg]);
        } finally {
            setIsLoading(false);
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(inputText);
        }
    };

    const saveConfig = async () => {
        setConfigSaving(true);
        try {
            const res = await api.post('/api/v1/chatbot/config', config);
            setEmbedCode(res.data.embed_code || '');
            setConfigMode(false);
        } catch {
            alert('Konfigürasyon kaydedilemedi');
        } finally {
            setConfigSaving(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="p-6 max-w-6xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-white">🤖 AI Chatbot</h1>
                        <p className="text-gray-400 mt-1">Web sitenize entegre edilebilir akıllı satış asistanı</p>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => { setActiveTab('chat'); setConfigMode(false); setSelectedConv(null); }}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'chat' ? 'bg-blue-600 text-white' : 'bg-white/10 text-gray-300 hover:bg-white/20'}`}
                        >
                            💬 Sohbet
                        </button>
                        <button
                            onClick={() => setActiveTab('history')}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'history' ? 'bg-blue-600 text-white' : 'bg-white/10 text-gray-300 hover:bg-white/20'}`}
                        >
                            📋 Sohbet Geçmişi
                        </button>
                        <button
                            onClick={() => setConfigMode(!configMode)}
                            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors"
                        >
                            ⚙️ Ayarlar
                        </button>
                    </div>
                </div>

                {/* Config Panel */}
                {configMode && (
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
                        <h2 className="text-white font-semibold text-lg">Bot Yapılandırması</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Bot Adı</label>
                                <input
                                    value={config.bot_name}
                                    onChange={e => setConfig(p => ({ ...p, bot_name: e.target.value }))}
                                    className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500/50"
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Lead Hedefi</label>
                                <select
                                    value={config.goal}
                                    onChange={e => setConfig(p => ({ ...p, goal: e.target.value }))}
                                    className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none"
                                >
                                    <option value="email">Sadece E-mail</option>
                                    <option value="phone">Sadece Telefon</option>
                                    <option value="both">E-mail + Telefon</option>
                                </select>
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-sm text-gray-400 mb-1">Karşılama Mesajı</label>
                                <textarea
                                    value={config.welcome_message}
                                    onChange={e => setConfig(p => ({ ...p, welcome_message: e.target.value }))}
                                    rows={2}
                                    className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500/50 resize-none"
                                />
                            </div>
                        </div>
                        <button
                            onClick={saveConfig}
                            disabled={configSaving}
                            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors"
                        >
                            {configSaving ? 'Kaydediliyor...' : '💾 Kaydet'}
                        </button>
                        {embedCode && (
                            <div className="mt-4">
                                <label className="block text-sm text-gray-400 mb-2">📋 Embed Kodu (sitenize ekleyin)</label>
                                <code className="block bg-black/40 rounded-lg p-3 text-xs text-green-400 font-mono break-all">{embedCode}</code>
                            </div>
                        )}
                    </div>
                )}

                {/* CHAT TAB */}
                {activeTab === 'chat' && !configMode && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Chat Window */}
                        <div className="bg-white/5 border border-white/10 rounded-2xl flex flex-col" style={{ height: '600px' }}>
                            <div className="flex items-center gap-3 p-4 border-b border-white/10">
                                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-lg">🤖</div>
                                <div>
                                    <div className="text-white font-medium text-sm">{config.bot_name}</div>
                                    <div className="flex items-center gap-1 text-xs text-green-400">
                                        <span className="w-2 h-2 bg-green-400 rounded-full inline-block"></span>
                                        Çevrimiçi
                                    </div>
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                                {messages.map(msg => (
                                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-xs lg:max-w-sm px-3 py-2 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-br-sm'
                                            : 'bg-white/10 text-gray-200 rounded-bl-sm'
                                            }`}>
                                            {msg.content}
                                            <div className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-200' : 'text-gray-500'}`}>
                                                {msg.timestamp.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                {isLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-white/10 text-gray-200 px-4 py-3 rounded-2xl rounded-bl-sm text-sm">
                                            <span className="animate-pulse">●●●</span>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            <div className="p-4 border-t border-white/10">
                                <div className="flex gap-2">
                                    <input
                                        ref={inputRef}
                                        value={inputText}
                                        onChange={e => setInputText(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        placeholder="Mesaj yazın... (Enter ile gönderin)"
                                        disabled={isLoading}
                                        className="flex-1 bg-black/30 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500/50 disabled:opacity-50"
                                    />
                                    <button
                                        onClick={() => sendMessage(inputText)}
                                        disabled={!inputText.trim() || isLoading}
                                        className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-xl text-sm font-medium transition-colors"
                                    >
                                        ➤
                                    </button>
                                </div>
                                <p className="text-xs text-gray-600 mt-2 text-center">Groq Llama 3.1 tarafından desteklenmektedir</p>
                            </div>
                        </div>

                        {/* Right Panel */}
                        <div className="space-y-4">
                            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 space-y-3">
                                <h3 className="text-white font-medium">📊 Oturum Bilgisi</h3>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Oturum ID</span>
                                        <span className="text-gray-300 font-mono text-xs">{sessionId.slice(0, 8)}...</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Mesaj sayısı</span>
                                        <span className="text-white">{messages.length}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">AI Sağlayıcı</span>
                                        <span className="text-green-400">Groq Llama 3.1</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Hedef</span>
                                        <span className="text-blue-400">{config.goal === 'email' ? 'E-mail toplama' : config.goal === 'phone' ? 'Telefon toplama' : 'İkisi de'}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 space-y-3">
                                <h3 className="text-white font-medium">💡 Hızlı Test</h3>
                                <div className="space-y-2">
                                    {['Merhaba, ürünlerinizi görmek istiyorum', 'Fiyat bilgisi alabilir miyim?', 'Email: test@example.com'].map(q => (
                                        <button
                                            key={q}
                                            onClick={() => sendMessage(q)}
                                            disabled={isLoading}
                                            className="w-full text-left px-3 py-2 bg-black/30 hover:bg-black/50 disabled:opacity-50 text-gray-300 text-xs rounded-lg transition-colors border border-white/5"
                                        >
                                            {q}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* HISTORY TAB */}
                {activeTab === 'history' && !configMode && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Left: conversation list */}
                        <div className="bg-white/5 border border-white/10 rounded-2xl flex flex-col" style={{ maxHeight: '650px' }}>
                            <div className="p-4 border-b border-white/10 flex items-center justify-between">
                                <h2 className="text-white font-semibold">Geçmiş Sohbetler</h2>
                                <button onClick={fetchHistory} className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                                    🔄 Yenile
                                </button>
                            </div>
                            <div className="flex-1 overflow-y-auto p-2 space-y-2">
                                {historyLoading && (
                                    <div className="text-center text-gray-500 py-8 text-sm">Yükleniyor...</div>
                                )}
                                {!historyLoading && history.length === 0 && (
                                    <div className="text-center text-gray-500 py-8 text-sm">Henüz sohbet geçmişi yok</div>
                                )}
                                {history.map(item => (
                                    <button
                                        key={item.session_id}
                                        onClick={() => loadConversation(item.session_id)}
                                        className={`w-full text-left p-3 rounded-xl transition-colors border ${selectedConv?.session_id === item.session_id
                                            ? 'bg-blue-600/20 border-blue-500/40'
                                            : 'bg-black/20 border-white/5 hover:bg-white/10'
                                            }`}
                                    >
                                        <div className="flex items-start justify-between gap-2">
                                            <div className="flex-1 min-w-0">
                                                <p className="text-gray-200 text-xs truncate">
                                                    {item.first_message || '(Mesaj yok)'}
                                                </p>
                                                <div className="flex gap-2 mt-1">
                                                    <span className="text-gray-500 text-xs">{item.message_count} mesaj</span>
                                                    {item.collected_data?.email && (
                                                        <span className="text-green-400 text-xs">✉ {item.collected_data.email}</span>
                                                    )}
                                                    {item.collected_data?.phone && (
                                                        <span className="text-blue-400 text-xs">📞</span>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="shrink-0 text-right">
                                                {item.is_completed && (
                                                    <span className="text-xs bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded">✓</span>
                                                )}
                                                <p className="text-gray-600 text-xs mt-1">
                                                    {item.created_at
                                                        ? new Date(item.created_at).toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit' })
                                                        : ''}
                                                </p>
                                            </div>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Right: selected conversation messages */}
                        <div className="bg-white/5 border border-white/10 rounded-2xl flex flex-col" style={{ maxHeight: '650px' }}>
                            {!selectedConv ? (
                                <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                                    ← Bir sohbet seçin
                                </div>
                            ) : (
                                <>
                                    <div className="p-4 border-b border-white/10">
                                        <p className="text-white text-sm font-medium">Sohbet Detayı</p>
                                        <p className="text-gray-500 text-xs font-mono">{selectedConv.session_id.slice(0, 16)}...</p>
                                    </div>
                                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                                        {selectedConv.messages.map(msg => (
                                            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                                <div className={`max-w-xs px-3 py-2 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                                    ? 'bg-blue-600 text-white rounded-br-sm'
                                                    : 'bg-white/10 text-gray-200 rounded-bl-sm'
                                                    }`}>
                                                    {msg.content}
                                                    <div className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-200' : 'text-gray-500'}`}>
                                                        {msg.timestamp.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
