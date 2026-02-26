'use client';

import { useState, useEffect, useRef } from 'react';
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
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        // Başlangıç mesajı
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
        } catch (err: any) {
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
        } catch (err) {
            alert('Konfigürasyon kaydedilemedi');
        } finally {
            setConfigSaving(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="p-6 max-w-6xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-white">🤖 AI Chatbot</h1>
                        <p className="text-gray-400 mt-1">Web sitenize entegre edilebilir akıllı satış asistanı</p>
                    </div>
                    <button
                        onClick={() => setConfigMode(!configMode)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                        {configMode ? '💬 Sohbete Dön' : '⚙️ Bot Ayarları'}
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* LEFT: Config or Chat */}
                    {configMode ? (
                        <div className="lg:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
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
                                    <code className="block bg-black/40 rounded-lg p-3 text-xs text-green-400 font-mono break-all">
                                        {embedCode}
                                    </code>
                                </div>
                            )}
                        </div>
                    ) : (
                        <>
                            {/* Chat Window */}
                            <div className="bg-white/5 border border-white/10 rounded-2xl flex flex-col" style={{ height: '600px' }}>
                                {/* Chat Header */}
                                <div className="flex items-center gap-3 p-4 border-b border-white/10">
                                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-lg">
                                        🤖
                                    </div>
                                    <div>
                                        <div className="text-white font-medium text-sm">{config.bot_name}</div>
                                        <div className="flex items-center gap-1 text-xs text-green-400">
                                            <span className="w-2 h-2 bg-green-400 rounded-full inline-block"></span>
                                            Çevrimiçi
                                        </div>
                                    </div>
                                </div>

                                {/* Messages */}
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

                                {/* Input */}
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

                            {/* Right: Stats/Info */}
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
                        </>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}
