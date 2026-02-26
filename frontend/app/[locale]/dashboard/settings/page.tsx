'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import api from '@/lib/api';

interface Setting {
    key_name: string;
    key_value: string | null;
    description: string | null;
    category: string | null;
    is_sensitive: boolean;
    is_active: boolean;
}

const CATEGORIES = [
    { id: 'ai', label: '🤖 AI Servisleri', color: 'purple' },
    { id: 'maps', label: '🗺️ Harita & Konum', color: 'blue' },
    { id: 'scraper', label: '🔍 Scraping & Proxy', color: 'orange' },
    { id: 'email', label: '📧 E-Mail', color: 'green' },
    { id: 'system', label: '⚙️ Sistem', color: 'gray' },
];

export default function SettingsPage() {
    const [settings, setSettings] = useState<Setting[]>([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState<string | null>(null);
    const [testing, setTesting] = useState<string | null>(null);
    const [testResults, setTestResults] = useState<Record<string, { status: string; message: string }>>({});
    const [editValues, setEditValues] = useState<Record<string, string>>({});
    const [showValues, setShowValues] = useState<Record<string, boolean>>({});
    const [health, setHealth] = useState<Record<string, string>>({});
    const [activeTab, setActiveTab] = useState('ai');
    const [successMsg, setSuccessMsg] = useState<string | null>(null);

    useEffect(() => {
        fetchSettings();
        fetchHealth();
    }, []);

    const fetchSettings = async () => {
        try {
            const res = await api.get('/api/v1/admin/settings');
            setSettings(res.data);
        } catch (err) {
            console.error('Ayarlar yüklenemedi:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchHealth = async () => {
        try {
            const res = await api.get('/api/v1/admin/health');
            setHealth(res.data);
        } catch (err) {
            console.error('Sağlık durumu alınamadı');
        }
    };

    const handleSave = async (keyName: string) => {
        const value = editValues[keyName];
        if (value === undefined) return;

        setSaving(keyName);
        try {
            await api.put(`/api/v1/admin/settings/${keyName}`, { key_value: value });
            await fetchSettings();
            setEditValues(prev => { const n = { ...prev }; delete n[keyName]; return n; });
            setSuccessMsg(`${keyName} güncellendi ✅`);
            setTimeout(() => setSuccessMsg(null), 3000);
        } catch (err) {
            alert('Kaydetme hatası');
        } finally {
            setSaving(null);
        }
    };

    const handleTest = async (keyName: string) => {
        setTesting(keyName);
        try {
            const res = await api.post(`/api/v1/admin/settings/test/${keyName}`);
            setTestResults(prev => ({ ...prev, [keyName]: res.data }));
        } catch (err) {
            setTestResults(prev => ({ ...prev, [keyName]: { status: 'error', message: 'Test başarısız' } }));
        } finally {
            setTesting(null);
        }
    };

    const filteredSettings = settings.filter(s => s.category === activeTab);

    const getCategoryColor = (cat: string) => {
        const colors: Record<string, string> = {
            ai: 'from-purple-500/20 to-purple-600/10 border-purple-500/30',
            maps: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
            scraper: 'from-orange-500/20 to-orange-600/10 border-orange-500/30',
            email: 'from-green-500/20 to-green-600/10 border-green-500/30',
            system: 'from-gray-500/20 to-gray-600/10 border-gray-500/30',
        };
        return colors[cat] || colors.system;
    };

    return (
        <DashboardLayout>
            <div className="p-6 max-w-5xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-white">⚙️ Sistem Ayarları</h1>
                        <p className="text-gray-400 mt-1">API anahtarları ve servis yapılandırmaları</p>
                    </div>
                    <button
                        onClick={() => { fetchSettings(); fetchHealth(); }}
                        className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm transition-colors"
                    >
                        🔄 Yenile
                    </button>
                </div>

                {successMsg && (
                    <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-3 text-green-400 text-sm">
                        {successMsg}
                    </div>
                )}

                {/* System Health */}
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                    <h2 className="text-white font-semibold mb-3">📊 Sistem Durumu</h2>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                        {Object.entries(health).map(([key, value]) => (
                            <div key={key} className="bg-black/30 rounded-lg p-3 text-center">
                                <div className="text-xs text-gray-400 mb-1">{key.replace(/_/g, ' ').toUpperCase()}</div>
                                <div className="text-sm font-medium text-white">{value}</div>
                            </div>
                        ))}
                        {Object.keys(health).length === 0 && (
                            <div className="col-span-5 text-gray-500 text-sm text-center py-2">Yükleniyor...</div>
                        )}
                    </div>
                </div>

                {/* Category Tabs */}
                <div className="flex gap-2 flex-wrap">
                    {CATEGORIES.map(cat => (
                        <button
                            key={cat.id}
                            onClick={() => setActiveTab(cat.id)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === cat.id
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white/5 hover:bg-white/10 text-gray-400'
                                }`}
                        >
                            {cat.label}
                        </button>
                    ))}
                </div>

                {/* Settings List */}
                {loading ? (
                    <div className="text-center py-12 text-gray-500">Yükleniyor...</div>
                ) : (
                    <div className="space-y-3">
                        {filteredSettings.map(setting => {
                            const isEditing = editValues[setting.key_name] !== undefined;
                            const testResult = testResults[setting.key_name];
                            const isSaving = saving === setting.key_name;
                            const isTesting = testing === setting.key_name;

                            return (
                                <div
                                    key={setting.key_name}
                                    className={`bg-gradient-to-br ${getCategoryColor(setting.category || 'system')} border rounded-xl p-4`}
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="font-mono text-sm font-bold text-white">{setting.key_name}</span>
                                                {setting.is_sensitive && (
                                                    <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full">
                                                        🔒 Şifreli
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-xs text-gray-400 mb-3">{setting.description}</p>

                                            {/* Input */}
                                            <div className="flex gap-2">
                                                <div className="relative flex-1">
                                                    <input
                                                        type={setting.is_sensitive && !showValues[setting.key_name] ? 'password' : 'text'}
                                                        value={isEditing ? editValues[setting.key_name] : (setting.key_value || '')}
                                                        onChange={e => setEditValues(prev => ({ ...prev, [setting.key_name]: e.target.value }))}
                                                        onFocus={() => {
                                                            if (!isEditing) {
                                                                setEditValues(prev => ({ ...prev, [setting.key_name]: '' }));
                                                            }
                                                        }}
                                                        placeholder={setting.key_value ? '••• (değiştirmek için tıkla)' : 'Buraya girin...'}
                                                        className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-blue-500/50 font-mono"
                                                    />
                                                    {setting.is_sensitive && (
                                                        <button
                                                            type="button"
                                                            onClick={() => setShowValues(prev => ({ ...prev, [setting.key_name]: !prev[setting.key_name] }))}
                                                            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 text-xs"
                                                        >
                                                            {showValues[setting.key_name] ? '🙈' : '👁️'}
                                                        </button>
                                                    )}
                                                </div>

                                                {isEditing && (
                                                    <>
                                                        <button
                                                            onClick={() => handleSave(setting.key_name)}
                                                            disabled={isSaving}
                                                            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
                                                        >
                                                            {isSaving ? '...' : '💾 Kaydet'}
                                                        </button>
                                                        <button
                                                            onClick={() => setEditValues(prev => { const n = { ...prev }; delete n[setting.key_name]; return n; })}
                                                            className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm transition-colors"
                                                        >
                                                            ✕
                                                        </button>
                                                    </>
                                                )}

                                                {!isEditing && setting.key_value && (
                                                    <button
                                                        onClick={() => handleTest(setting.key_name)}
                                                        disabled={isTesting}
                                                        className="px-3 py-2 bg-white/10 hover:bg-white/20 disabled:opacity-50 text-white rounded-lg text-sm transition-colors whitespace-nowrap"
                                                    >
                                                        {isTesting ? '...' : '🧪 Test'}
                                                    </button>
                                                )}
                                            </div>

                                            {/* Test Result */}
                                            {testResult && (
                                                <div className={`mt-2 text-xs px-3 py-1.5 rounded-lg ${testResult.status === 'success'
                                                        ? 'bg-green-500/20 text-green-400'
                                                        : testResult.status === 'error'
                                                            ? 'bg-red-500/20 text-red-400'
                                                            : 'bg-blue-500/20 text-blue-400'
                                                    }`}>
                                                    {testResult.message}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}

                        {filteredSettings.length === 0 && !loading && (
                            <div className="text-center py-8 text-gray-500">Bu kategoride ayar bulunamadı</div>
                        )}
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
