'use client';

import { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function authHeader() {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : '';
    return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
}

// ─── Types ──────────────────────────────────────────────────────
interface AppUser {
    id: number; email: string; full_name: string;
    is_active: boolean; is_superuser: boolean;
    subscription_tier: string; query_credits: number; created_at: string;
}
interface ApiSetting {
    key_name: string; key_value: string | null;
    description: string; category: string;
    is_sensitive: boolean; is_active: boolean;
}
interface Stats {
    users: { total: number; active: number; new_today: number };
    visitors: { total: number; today: number; this_week: number };
    subscription_distribution: Record<string, number>;
}
interface ModuleSummary {
    module: string; count: number; total_credits: number; last_used: string | null;
}
interface SearchHistory {
    query_type: string; count: number; total_credits: number;
}
interface RecentActivity {
    id: number; module: string; action: string;
    credits_used: number; status: string; created_at: string | null;
    meta_data?: Record<string, unknown>;
}
interface UserActivityData {
    user: AppUser;
    module_summary: ModuleSummary[];
    search_history: SearchHistory[];
    recent_activities: RecentActivity[];
    total_activities: number;
}

type Tab = 'overview' | 'users' | 'apis';

// ─── SVG Donut Chart ────────────────────────────────────────────
function DonutChart({ data, size = 140 }: { data: { label: string; value: number; color: string }[]; size?: number }) {
    const total = data.reduce((s, d) => s + d.value, 0);
    if (!total) return <div style={{ width: size, height: size, borderRadius: '50%', background: '#1a2844', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', fontSize: 12 }}>Veri yok</div>;

    const r = 45, cx = 50, cy = 50, stroke = 18;
    const circumference = 2 * Math.PI * r;
    let offset = 0;

    return (
        <svg width={size} height={size} viewBox="0 0 100 100">
            <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1a2844" strokeWidth={stroke} />
            {data.map((d, i) => {
                const pct = d.value / total;
                const dash = pct * circumference;
                const gap = circumference - dash;
                const startOffset = offset;
                offset += pct * circumference;
                return (
                    <circle key={i} cx={cx} cy={cy} r={r} fill="none"
                        stroke={d.color} strokeWidth={stroke}
                        strokeDasharray={`${dash} ${gap}`}
                        strokeDashoffset={-(startOffset - circumference / 4)}
                        style={{ transition: 'stroke-dasharray 0.6s ease' }}
                    />
                );
            })}
            <text x={cx} y={cy - 5} textAnchor="middle" fill="#f1f5f9" fontSize="14" fontWeight="bold">{total}</text>
            <text x={cx} y={cy + 10} textAnchor="middle" fill="#64748b" fontSize="7">toplam</text>
        </svg>
    );
}

// ─── Mini Bar Chart ─────────────────────────────────────────────
function MiniBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
    const pct = max ? (value / max) * 100 : 0;
    return (
        <div style={{ marginBottom: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: 12 }}>
                <span style={{ color: '#94a3b8' }}>{label}</span>
                <span style={{ color: '#f1f5f9', fontWeight: 700 }}>{value}</span>
            </div>
            <div style={{ height: 6, background: '#1a2844', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 3, transition: 'width 0.8s ease' }} />
            </div>
        </div>
    );
}

// ─── Stat Card ──────────────────────────────────────────────────
function StatCard({ icon, label, value, sub, color }: { icon: string; label: string; value: number | string; sub?: string; color: string }) {
    return (
        <div style={{
            background: 'linear-gradient(135deg, #0c1424, #111c32)',
            border: `1px solid ${color}33`, borderRadius: 16, padding: '22px 24px',
            position: 'relative', overflow: 'hidden',
        }}>
            <div style={{ position: 'absolute', top: -10, right: -10, fontSize: 64, opacity: 0.07 }}>{icon}</div>
            <div style={{ fontSize: 28, marginBottom: 6 }}>{icon}</div>
            <div style={{ fontSize: 36, fontWeight: 800, color, lineHeight: 1 }}>{value}</div>
            <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 6 }}>{label}</div>
            {sub && <div style={{ fontSize: 11, color: '#475569', marginTop: 4 }}>{sub}</div>}
        </div>
    );
}

// ─── Category config ────────────────────────────────────────────
const CAT_CONFIG: Record<string, { label: string; icon: string; color: string; desc: string }> = {
    ai: { label: 'AI Servisleri', icon: '🤖', color: '#a78bfa', desc: 'Chatbot ve görüntü analiz' },
    maps: { label: 'Harita', icon: '🗺️', color: '#22d3ee', desc: 'Google Maps entegrasyonu' },
    scraper: { label: 'Web Scraping', icon: '🕷️', color: '#fb923c', desc: 'Proxy ve scraping araçları' },
    email: { label: 'E-Posta', icon: '📧', color: '#34d399', desc: 'SMTP ve SendGrid ayarları' },
    system: { label: 'Sistem', icon: '⚙️', color: '#c9a227', desc: 'Güvenlik ve sistem ayarları' },
};

const MODULE_LABELS: Record<string, { label: string; icon: string; color: string }> = {
    search: { label: 'Ürün Arama', icon: '🔍', color: '#22d3ee' },
    chatbot: { label: 'AI Chatbot', icon: '🤖', color: '#a78bfa' },
    maps: { label: 'Harita Araştırma', icon: '🗺️', color: '#34d399' },
    contact: { label: 'İletişim Bulucu', icon: '📞', color: '#fb923c' },
    fairs: { label: 'Fuar Analizi', icon: '🎪', color: '#c9a227' },
    mail: { label: 'Otomatik Mail', icon: '📧', color: '#34d399' },
    b2b: { label: 'B2B Platformlar', icon: '🌐', color: '#22d3ee' },
    visitor: { label: 'Ziyaretçi Takip', icon: '👁', color: '#f472b6' },
    markets: { label: 'Pazar Analizi', icon: '📈', color: '#a78bfa' },
    marketplace: { label: 'Marketplace', icon: '🛒', color: '#fb923c' },
    scraping: { label: 'Web Scraping', icon: '🕷️', color: '#94a3b8' },
    product_search: { label: 'Ürün Arama', icon: '🔍', color: '#22d3ee' },
    company_search: { label: 'Şirket Arama', icon: '🏢', color: '#a78bfa' },
    map_scraping: { label: 'Harita Tarama', icon: '🗺️', color: '#34d399' },
    fair_search: { label: 'Fuar Arama', icon: '🎪', color: '#c9a227' },
    image_search: { label: 'Görsel Arama', icon: '🖼️', color: '#f472b6' },
};

const TIER_COLORS: Record<string, string> = { free: '#64748b', basic: '#34d399', pro: '#c9a227', enterprise: '#22d3ee' };
const STATUS_COLORS: Record<string, string> = { success: '#34d399', error: '#ef4444', pending: '#c9a227' };

const T = { bg: '#060b18', bg2: '#0c1424', bg3: '#111c32', gold: '#c9a227', goldL: '#e8c84a', goldD: 'rgba(201,162,39,0.12)', cyan: '#22d3ee', green: '#34d399', red: '#ef4444', t1: '#f1f5f9', t2: '#94a3b8', t3: '#475569', bd: 'rgba(255,255,255,0.06)', bdA: 'rgba(201,162,39,0.2)' };

// ─── Main Component ─────────────────────────────────────────────
export default function AdminPage() {
    const [tab, setTab] = useState<Tab>('overview');
    const [stats, setStats] = useState<Stats | null>(null);
    const [users, setUsers] = useState<AppUser[]>([]);
    const [userTotal, setUserTotal] = useState(0);
    const [settings, setSettings] = useState<ApiSetting[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [search, setSearch] = useState('');
    const [editUser, setEditUser] = useState<AppUser | null>(null);
    const [editCredits, setEditCredits] = useState('');
    const [editTier, setEditTier] = useState('');
    const [keyInputs, setKeyInputs] = useState<Record<string, string>>({});
    const [showKey, setShowKey] = useState<Record<string, boolean>>({});
    const [savingKey, setSavingKey] = useState('');
    const [testResults, setTestResults] = useState<Record<string, { status: string; message: string }>>({});
    const [toast, setToast] = useState('');
    // Aktivite modal
    const [activityUser, setActivityUser] = useState<UserActivityData | null>(null);
    const [activityLoading, setActivityLoading] = useState(false);

    const showToast = (msg: string) => { setToast(msg); setTimeout(() => setToast(''), 3500); };

    const fetchStats = useCallback(async () => {
        setLoading(true); setError('');
        const r = await fetch(`${API_URL}/api/v1/admin/stats`, { headers: authHeader() });
        if (r.ok) setStats(await r.json());
        else if (r.status === 403) setError('Bu sayfayı görüntülemek için admin yetkisi gereklidir.');
        setLoading(false);
    }, []);

    const fetchUsers = useCallback(async () => {
        setLoading(true);
        const r = await fetch(`${API_URL}/api/v1/admin/users?limit=200${search ? `&search=${encodeURIComponent(search)}` : ''}`, { headers: authHeader() });
        if (r.ok) { const d = await r.json(); setUsers(d.users); setUserTotal(d.total); }
        setLoading(false);
    }, [search]);

    const fetchSettings = useCallback(async () => {
        setLoading(true);
        const r = await fetch(`${API_URL}/api/v1/admin/settings`, { headers: authHeader() });
        if (r.ok) setSettings(await r.json());
        setLoading(false);
    }, []);

    const fetchUserActivity = async (userId: number) => {
        setActivityLoading(true);
        const r = await fetch(`${API_URL}/api/v1/admin/users/${userId}/activity`, { headers: authHeader() });
        if (r.ok) setActivityUser(await r.json());
        else showToast('❌ Aktivite verisi alınamadı');
        setActivityLoading(false);
    };

    useEffect(() => {
        if (tab === 'overview') fetchStats();
        else if (tab === 'users') fetchUsers();
        else if (tab === 'apis') fetchSettings();
    }, [tab, fetchStats, fetchUsers, fetchSettings]);

    const updateUser = async () => {
        if (!editUser) return;
        const body: Record<string, unknown> = {};
        if (editCredits !== '') body.query_credits = parseInt(editCredits);
        if (editTier) body.subscription_tier = editTier;
        const r = await fetch(`${API_URL}/api/v1/admin/users/${editUser.id}`, { method: 'PATCH', headers: authHeader(), body: JSON.stringify(body) });
        if (r.ok) { showToast('✅ Kullanıcı güncellendi'); setEditUser(null); fetchUsers(); }
        else showToast('❌ Güncelleme başarısız');
    };

    const toggleUserStatus = async (u: AppUser) => {
        const r = await fetch(`${API_URL}/api/v1/admin/users/${u.id}`, { method: 'PATCH', headers: authHeader(), body: JSON.stringify({ is_active: !u.is_active }) });
        if (r.ok) { showToast(u.is_active ? '⛔ Pasife alındı' : '✅ Aktif edildi'); fetchUsers(); }
    };

    const deleteUser = async (u: AppUser) => {
        if (!confirm(`"${u.email}" silinsin mi?`)) return;
        const r = await fetch(`${API_URL}/api/v1/admin/users/${u.id}`, { method: 'DELETE', headers: authHeader() });
        if (r.ok) { showToast('🗑️ Silindi'); fetchUsers(); }
    };

    const saveSetting = async (keyName: string) => {
        const val = keyInputs[keyName]?.trim();
        if (!val) return;
        setSavingKey(keyName);
        const r = await fetch(`${API_URL}/api/v1/admin/settings/${keyName}`, { method: 'PUT', headers: authHeader(), body: JSON.stringify({ key_value: val }) });
        if (r.ok) { showToast(`✅ ${keyName} kaydedildi`); setKeyInputs(p => ({ ...p, [keyName]: '' })); fetchSettings(); }
        else showToast('❌ Kaydetme başarısız');
        setSavingKey('');
    };

    const testSetting = async (keyName: string) => {
        setTestResults(p => ({ ...p, [keyName]: { status: 'testing', message: 'Test ediliyor...' } }));
        const r = await fetch(`${API_URL}/api/v1/admin/settings/test/${keyName}`, { method: 'POST', headers: authHeader() });
        if (r.ok) { const d = await r.json(); setTestResults(p => ({ ...p, [keyName]: d })); }
        else setTestResults(p => ({ ...p, [keyName]: { status: 'error', message: 'Test başarısız' } }));
    };

    const grouped = settings.reduce((acc, s) => { (acc[s.category] = acc[s.category] || []).push(s); return acc; }, {} as Record<string, ApiSetting[]>);
    const tierData = stats ? Object.entries(stats.subscription_distribution).map(([k, v]) => ({ label: k, value: v, color: TIER_COLORS[k] || '#475569' })) : [];

    return (
        <DashboardLayout>
            {/* Toast */}
            {toast && (
                <div style={{ position: 'fixed', top: 24, right: 24, zIndex: 9999, background: '#0c1424', border: `1px solid ${T.bdA}`, borderRadius: 12, padding: '12px 20px', color: T.t1, fontSize: 14, fontWeight: 600, boxShadow: '0 8px 32px rgba(0,0,0,0.6)', animation: 'fade 0.3s ease' }}>
                    {toast}
                </div>
            )}
            <style>{`@keyframes fade{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}} @keyframes spin{to{transform:rotate(360deg)}}`}</style>

            <div style={{ padding: '28px 28px', fontFamily: "'Plus Jakarta Sans',sans-serif", color: T.t1, minHeight: '100vh', background: T.bg }}>

                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
                    <div>
                        <h1 style={{ fontSize: 28, fontWeight: 800, margin: 0, background: `linear-gradient(135deg, ${T.gold}, ${T.goldL})`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                            ⚙️ Admin Paneli
                        </h1>
                        <p style={{ color: T.t3, fontSize: 13, marginTop: 4 }}>Sistem yönetimi, kullanıcılar ve API yapılandırması</p>
                    </div>
                    <div style={{ padding: '8px 16px', background: `${T.green}22`, border: `1px solid ${T.green}44`, borderRadius: 10, fontSize: 12, color: T.green, fontWeight: 600 }}>
                        🔒 Güvenli Bağlantı
                    </div>
                </div>

                {/* Tab Bar */}
                <div style={{ display: 'flex', gap: 4, marginBottom: 28, background: T.bg2, border: `1px solid ${T.bd}`, borderRadius: 14, padding: 4, width: 'fit-content' }}>
                    {([['overview', '📊', 'Genel Bakış'], ['users', '👥', 'Kullanıcılar'], ['apis', '🔑', 'API Yönetimi']] as [Tab, string, string][]).map(([t, icon, label]) => (
                        <button key={t} onClick={() => setTab(t)} style={{
                            padding: '10px 24px', border: 'none', borderRadius: 10, cursor: 'pointer',
                            fontSize: 14, fontWeight: 600, transition: 'all 0.2s',
                            background: tab === t ? `linear-gradient(135deg, ${T.gold}, ${T.goldL})` : 'transparent',
                            color: tab === t ? T.bg : T.t3,
                        }}>{icon} {label}</button>
                    ))}
                </div>

                {error && (
                    <div style={{ background: '#ef444411', border: `1px solid ${T.red}44`, borderRadius: 12, padding: '14px 20px', marginBottom: 24, color: T.red, fontSize: 14 }}>
                        🔒 {error}
                    </div>
                )}

                {/* ── OVERVIEW TAB ─────────────────────────────────── */}
                {tab === 'overview' && (
                    <div>
                        {loading ? <LoadingSpinner /> : stats ? (
                            <>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 16, marginBottom: 28 }}>
                                    <StatCard icon="👥" label="Toplam Kullanıcı" value={stats.users.total} color={T.cyan} />
                                    <StatCard icon="✅" label="Aktif Kullanıcı" value={stats.users.active} sub={`${Math.round(stats.users.active / Math.max(stats.users.total, 1) * 100)}% aktif`} color={T.green} />
                                    <StatCard icon="🆕" label="Bugün Katılan" value={stats.users.new_today} color={T.gold} />
                                    <StatCard icon="👁" label="Toplam Ziyaret" value={stats.visitors.total} color="#a78bfa" />
                                    <StatCard icon="📅" label="Bugünkü Ziyaret" value={stats.visitors.today} color={T.cyan} />
                                    <StatCard icon="📈" label="Haftalık Ziyaret" value={stats.visitors.this_week} color={T.green} />
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                                    <div style={{ background: T.bg2, border: `1px solid ${T.bd}`, borderRadius: 18, padding: 28 }}>
                                        <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 700 }}>📦 Abonelik Dağılımı</h3>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
                                            <DonutChart data={tierData} size={140} />
                                            <div style={{ flex: 1 }}>
                                                {tierData.map(d => (
                                                    <div key={d.label} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                                                        <div style={{ width: 10, height: 10, borderRadius: '50%', background: d.color, flexShrink: 0 }} />
                                                        <span style={{ fontSize: 13, color: T.t2, flex: 1, textTransform: 'capitalize' }}>{d.label}</span>
                                                        <span style={{ fontSize: 14, fontWeight: 700, color: d.color }}>{d.value}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ background: T.bg2, border: `1px solid ${T.bd}`, borderRadius: 18, padding: 28 }}>
                                        <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 700 }}>📈 Ziyaretçi İstatistikleri</h3>
                                        <MiniBar label="Bugün" value={stats.visitors.today} max={stats.visitors.total} color={T.gold} />
                                        <MiniBar label="Bu Hafta" value={stats.visitors.this_week} max={stats.visitors.total} color={T.cyan} />
                                        <MiniBar label="Toplam" value={stats.visitors.total} max={stats.visitors.total} color="#a78bfa" />
                                        <div style={{ marginTop: 20, padding: '12px 16px', background: `${T.green}11`, borderRadius: 10, border: `1px solid ${T.green}22` }}>
                                            <div style={{ fontSize: 12, color: T.t3 }}>Ortalama Günlük Ziyaretçi</div>
                                            <div style={{ fontSize: 22, fontWeight: 800, color: T.green, marginTop: 2 }}>
                                                {stats.visitors.this_week > 0 ? Math.round(stats.visitors.this_week / 7) : 0}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ background: T.bg2, border: `1px solid ${T.bd}`, borderRadius: 18, padding: 28 }}>
                                        <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 700 }}>👥 Kullanıcı Durumu</h3>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
                                            <DonutChart data={[
                                                { label: 'Aktif', value: stats.users.active, color: T.green },
                                                { label: 'Pasif', value: stats.users.total - stats.users.active, color: '#334155' },
                                            ]} size={120} />
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontSize: 13, color: T.t3, marginBottom: 8 }}>Aktif / Toplam</div>
                                                <div style={{ fontSize: 32, fontWeight: 800, color: T.green }}>{stats.users.active}<span style={{ fontSize: 16, color: T.t3 }}>/{stats.users.total}</span></div>
                                                <div style={{ marginTop: 10, fontSize: 12, color: T.t3 }}>Bugün +{stats.users.new_today} yeni</div>
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ background: T.bg2, border: `1px solid ${T.bd}`, borderRadius: 18, padding: 28 }}>
                                        <h3 style={{ margin: '0 0 20px', fontSize: 16, fontWeight: 700 }}>🔑 API Durumu</h3>
                                        {Object.entries(CAT_CONFIG).map(([cat, cfg]) => {
                                            const catSettings = settings.filter(s => s.category === cat);
                                            const configured = catSettings.filter(s => s.key_value).length;
                                            const total = catSettings.length;
                                            return (
                                                <div key={cat} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                                                    <span style={{ fontSize: 16 }}>{cfg.icon}</span>
                                                    <span style={{ flex: 1, fontSize: 13, color: T.t2 }}>{cfg.label}</span>
                                                    <span style={{ fontSize: 12, padding: '3px 8px', borderRadius: 6, background: configured > 0 ? `${T.green}22` : `${T.red}22`, color: configured > 0 ? T.green : T.red }}>
                                                        {total > 0 ? `${configured}/${total}` : '—'}
                                                    </span>
                                                </div>
                                            );
                                        })}
                                        <button onClick={() => setTab('apis')} style={{ marginTop: 14, width: '100%', padding: '10px', background: T.goldD, border: `1px solid ${T.bdA}`, borderRadius: 10, color: T.gold, fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>🔑 API Yönetimine Git →</button>
                                    </div>
                                </div>
                            </>
                        ) : null}
                    </div>
                )}

                {/* ── USERS TAB ─────────────────────────────────────── */}
                {tab === 'users' && (
                    <div>
                        <div style={{ display: 'flex', gap: 12, marginBottom: 18, alignItems: 'center' }}>
                            <div style={{ flex: 1, display: 'flex', gap: 0, background: T.bg2, border: `1px solid ${T.bd}`, borderRadius: 12, overflow: 'hidden' }}>
                                <span style={{ padding: '10px 14px', fontSize: 16 }}>🔍</span>
                                <input value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && fetchUsers()} placeholder="Email veya ad ile ara..." style={{ flex: 1, padding: '10px 4px', background: 'transparent', border: 'none', color: T.t1, fontSize: 14, outline: 'none' }} />
                            </div>
                            <button onClick={fetchUsers} style={{ padding: '10px 20px', background: T.goldD, border: `1px solid ${T.bdA}`, borderRadius: 12, color: T.gold, cursor: 'pointer', fontSize: 14, fontWeight: 600 }}>Ara</button>
                            <span style={{ color: T.t3, fontSize: 13 }}>Toplam: <strong style={{ color: T.t1 }}>{userTotal}</strong></span>
                        </div>

                        {loading ? <LoadingSpinner /> : (
                            <div style={{ background: T.bg2, border: `1px solid ${T.bd}`, borderRadius: 18, overflow: 'hidden' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ background: `${T.bg3}cc` }}>
                                            {['#', 'Kullanıcı', 'Paket', 'Kredi', 'Durum', 'Kayıt Tarihi', 'İşlemler'].map(h => (
                                                <th key={h} style={{ padding: '13px 16px', textAlign: 'left', fontSize: 11, fontWeight: 700, color: T.t3, textTransform: 'uppercase', letterSpacing: 1, borderBottom: `1px solid ${T.bd}` }}>{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {users.map((u, idx) => (
                                            <tr key={u.id} style={{ borderBottom: `1px solid ${T.bd}22`, transition: 'background 0.15s' }}>
                                                <td style={{ padding: '12px 16px', fontSize: 12, color: T.t3 }}>{idx + 1}</td>
                                                <td style={{ padding: '12px 16px' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                                        <div style={{ width: 32, height: 32, borderRadius: 10, background: `linear-gradient(135deg, ${T.gold}33, ${T.cyan}33)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700, color: T.t1 }}>{(u.full_name || u.email)[0].toUpperCase()}</div>
                                                        <div>
                                                            <div style={{ fontSize: 14, fontWeight: 600, color: T.t1 }}>{u.full_name || '—'} {u.is_superuser && <span style={{ fontSize: 10, background: `${T.gold}33`, color: T.gold, padding: '2px 6px', borderRadius: 4, marginLeft: 4 }}>★ ADMIN</span>}</div>
                                                            <div style={{ fontSize: 12, color: T.t3 }}>{u.email}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td style={{ padding: '12px 16px' }}>
                                                    <span style={{ padding: '4px 10px', borderRadius: 6, fontSize: 12, fontWeight: 600, background: `${TIER_COLORS[u.subscription_tier] || T.t3}22`, color: TIER_COLORS[u.subscription_tier] || T.t3 }}>{u.subscription_tier}</span>
                                                </td>
                                                <td style={{ padding: '12px 16px', fontSize: 15, fontWeight: 800, color: T.cyan }}>{u.query_credits}</td>
                                                <td style={{ padding: '12px 16px' }}>
                                                    <span style={{ padding: '4px 10px', borderRadius: 6, fontSize: 12, fontWeight: 600, background: u.is_active ? '#34d39922' : '#ef444422', color: u.is_active ? T.green : T.red }}>{u.is_active ? '● Aktif' : '○ Pasif'}</span>
                                                </td>
                                                <td style={{ padding: '12px 16px', fontSize: 12, color: T.t3 }}>{u.created_at ? new Date(u.created_at).toLocaleDateString('tr-TR') : '—'}</td>
                                                <td style={{ padding: '12px 16px' }}>
                                                    <div style={{ display: 'flex', gap: 6 }}>
                                                        <ActionBtn onClick={() => fetchUserActivity(u.id)} color={T.cyan} icon="📊" title="Kullanım Detayı" />
                                                        <ActionBtn onClick={() => { setEditUser(u); setEditCredits(String(u.query_credits)); setEditTier(u.subscription_tier); }} color={T.gold} icon="✏️" title="Düzenle" />
                                                        <ActionBtn onClick={() => toggleUserStatus(u)} color={u.is_active ? T.red : T.green} icon={u.is_active ? '⛔' : '✅'} title={u.is_active ? 'Pasife Al' : 'Aktif Et'} />
                                                        <ActionBtn onClick={() => deleteUser(u)} color={T.red} icon="🗑️" title="Sil" />
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {/* Edit Modal */}
                        {editUser && (
                            <Modal title={`✏️ ${editUser.email}`} onClose={() => setEditUser(null)}>
                                <label style={{ fontSize: 12, color: T.t3, display: 'block', marginBottom: 5 }}>Sorgu Kredisi</label>
                                <input type="number" value={editCredits} onChange={e => setEditCredits(e.target.value)} style={inputStyle(T)} />
                                <label style={{ fontSize: 12, color: T.t3, display: 'block', margin: '14px 0 5px' }}>Abonelik Paketi</label>
                                <select value={editTier} onChange={e => setEditTier(e.target.value)} style={inputStyle(T)}>
                                    {['free', 'basic', 'pro', 'enterprise'].map(t => <option key={t} value={t}>{t}</option>)}
                                </select>
                                <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
                                    <button onClick={updateUser} style={{ flex: 1, padding: 12, background: `linear-gradient(135deg, ${T.gold}, ${T.goldL})`, border: 'none', borderRadius: 10, color: T.bg, fontWeight: 700, fontSize: 14, cursor: 'pointer' }}>Kaydet</button>
                                    <button onClick={() => setEditUser(null)} style={{ flex: 1, padding: 12, background: T.bg3, border: `1px solid ${T.bd}`, borderRadius: 10, color: T.t2, fontWeight: 600, fontSize: 14, cursor: 'pointer' }}>İptal</button>
                                </div>
                            </Modal>
                        )}

                        {/* Activity Detail Modal */}
                        {(activityLoading || activityUser) && (
                            <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', zIndex: 999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }} onClick={e => { if (e.target === e.currentTarget) { setActivityUser(null); } }}>
                                <div style={{ background: T.bg2, border: '1px solid rgba(34,211,238,0.25)', borderRadius: 22, padding: 28, width: '100%', maxWidth: 840, maxHeight: '88vh', overflowY: 'auto', boxShadow: '0 32px 100px rgba(0,0,0,0.8)' }}>
                                    {activityLoading ? <LoadingSpinner /> : activityUser ? (
                                        <>
                                            {/* User header */}
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 22 }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                                                    <div style={{ width: 48, height: 48, borderRadius: 14, background: `linear-gradient(135deg, ${T.gold}44, ${T.cyan}44)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, fontWeight: 800, color: T.t1, flexShrink: 0 }}>
                                                        {(activityUser.user.full_name || activityUser.user.email)[0].toUpperCase()}
                                                    </div>
                                                    <div>
                                                        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: T.t1 }}>{activityUser.user.full_name || '—'}</h2>
                                                        <div style={{ fontSize: 13, color: T.cyan, marginTop: 2 }}>{activityUser.user.email}</div>
                                                        <div style={{ display: 'flex', gap: 8, marginTop: 5, flexWrap: 'wrap' }}>
                                                            <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 6, background: `${TIER_COLORS[activityUser.user.subscription_tier] || T.t3}22`, color: TIER_COLORS[activityUser.user.subscription_tier] || T.t3, fontWeight: 700 }}>{activityUser.user.subscription_tier.toUpperCase()}</span>
                                                            <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 6, background: activityUser.user.is_active ? `${T.green}22` : `${T.red}22`, color: activityUser.user.is_active ? T.green : T.red, fontWeight: 600 }}>{activityUser.user.is_active ? '● Aktif' : '○ Pasif'}</span>
                                                            <span style={{ fontSize: 10, color: T.t3 }}>Kayıt: {activityUser.user.created_at ? new Date(activityUser.user.created_at).toLocaleDateString('tr-TR') : '—'}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <button onClick={() => setActivityUser(null)} style={{ background: `${T.red}22`, border: `1px solid ${T.red}44`, borderRadius: 8, width: 32, height: 32, fontSize: 14, cursor: 'pointer', color: T.red, flexShrink: 0 }}>✕</button>
                                            </div>

                                            {/* Summary Cards — 4 columns */}
                                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginBottom: 22 }}>
                                                {(() => {
                                                    const totalCreditsUsed = activityUser.module_summary.reduce((s, m) => s + m.total_credits, 0);
                                                    const successCount = activityUser.recent_activities.filter(a => a.status === 'success').length;
                                                    const successRate = activityUser.recent_activities.length > 0
                                                        ? Math.round(successCount / activityUser.recent_activities.length * 100)
                                                        : null;
                                                    return [
                                                        { icon: '🔢', label: 'Toplam İşlem', value: activityUser.total_activities, color: T.cyan, sub: `${activityUser.module_summary.length} farklı modül` },
                                                        { icon: '💳', label: 'Harcanan Kredi', value: totalCreditsUsed, color: T.gold, sub: 'Tüm zamanlar' },
                                                        { icon: '🏦', label: 'Kalan Kredi', value: activityUser.user.query_credits.toLocaleString('tr-TR'), color: T.green, sub: 'Güncel bakiye' },
                                                        { icon: '✅', label: 'Başarı Oranı', value: successRate !== null ? `%${successRate}` : '—', color: '#a78bfa', sub: `${successCount}/${activityUser.recent_activities.length} istek` },
                                                    ].map(c => (
                                                        <div key={c.label} style={{ background: T.bg3, border: `1px solid ${c.color}33`, borderRadius: 14, padding: '14px 16px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
                                                            <div style={{ position: 'absolute', top: -8, right: -8, fontSize: 42, opacity: 0.06 }}>{c.icon}</div>
                                                            <div style={{ fontSize: 18, marginBottom: 2 }}>{c.icon}</div>
                                                            <div style={{ fontSize: 22, fontWeight: 800, color: c.color, lineHeight: 1 }}>{c.value}</div>
                                                            <div style={{ fontSize: 11, color: T.t3, marginTop: 4 }}>{c.label}</div>
                                                            <div style={{ fontSize: 10, color: T.t3, marginTop: 2, opacity: 0.7 }}>{c.sub}</div>
                                                        </div>
                                                    ));
                                                })()}
                                            </div>

                                            {/* Module Usage — donut + horizontal bars */}
                                            {activityUser.module_summary.length > 0 ? (
                                                <div style={{ background: T.bg3, borderRadius: 16, padding: '18px 20px', marginBottom: 20, border: `1px solid ${T.bd}` }}>
                                                    <h3 style={{ margin: '0 0 16px', fontSize: 13, fontWeight: 700, color: T.t2, textTransform: 'uppercase', letterSpacing: 1 }}>Modül Kullanımı</h3>
                                                    <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
                                                        <div style={{ flexShrink: 0 }}>
                                                            <DonutChart data={activityUser.module_summary.map(s => ({
                                                                label: MODULE_LABELS[s.module]?.label || s.module,
                                                                value: s.count,
                                                                color: MODULE_LABELS[s.module]?.color || '#64748b'
                                                            }))} size={110} />
                                                        </div>
                                                        <div style={{ flex: 1, minWidth: 0 }}>
                                                            {[...activityUser.module_summary].sort((a, b) => b.count - a.count).map(s => {
                                                                const cfg = MODULE_LABELS[s.module];
                                                                const maxCount = Math.max(...activityUser.module_summary.map(x => x.count));
                                                                const pct = maxCount > 0 ? (s.count / maxCount) * 100 : 0;
                                                                const lastUsedStr = s.last_used
                                                                    ? new Date(s.last_used).toLocaleString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
                                                                    : null;
                                                                return (
                                                                    <div key={s.module} style={{ marginBottom: 11 }}>
                                                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                                                            <span style={{ fontSize: 12, color: T.t1, display: 'flex', alignItems: 'center', gap: 5 }}>
                                                                                <span>{cfg?.icon || '•'}</span>
                                                                                <span>{cfg?.label || s.module}</span>
                                                                            </span>
                                                                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                                                                {s.total_credits > 0 && <span style={{ fontSize: 10, color: T.gold }}>{s.total_credits} kr</span>}
                                                                                {lastUsedStr && <span style={{ fontSize: 10, color: T.t3 }}>{lastUsedStr}</span>}
                                                                                <span style={{ fontSize: 13, fontWeight: 800, color: cfg?.color || T.t1, minWidth: 28, textAlign: 'right' }}>{s.count}x</span>
                                                                            </div>
                                                                        </div>
                                                                        <div style={{ height: 5, background: '#1a2844', borderRadius: 3, overflow: 'hidden' }}>
                                                                            <div style={{ height: '100%', width: `${pct}%`, background: cfg?.color || T.cyan, borderRadius: 3, transition: 'width 0.8s ease' }} />
                                                                        </div>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div style={{ textAlign: 'center', padding: '30px', color: T.t3, fontSize: 13, background: T.bg3, borderRadius: 14, marginBottom: 20, border: `1px solid ${T.bd}` }}>
                                                    📭 Henüz hiç modül kullanımı kaydedilmemiş
                                                </div>
                                            )}

                                            {/* Recent Activities Table */}
                                            {activityUser.recent_activities.length > 0 && (
                                                <div>
                                                    <h3 style={{ margin: '0 0 12px', fontSize: 13, fontWeight: 700, color: T.t2, textTransform: 'uppercase', letterSpacing: 1 }}>
                                                        Son Aktiviteler
                                                        <span style={{ fontSize: 11, color: T.t3, fontWeight: 400, textTransform: 'none', marginLeft: 8 }}>{activityUser.recent_activities.length} kayıt</span>
                                                    </h3>
                                                    <div style={{ background: T.bg3, borderRadius: 14, overflow: 'hidden', border: `1px solid ${T.bd}` }}>
                                                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                            <thead>
                                                                <tr style={{ background: `${T.bg}cc` }}>
                                                                    {['Modül', 'İşlem Açıklaması', 'Meta Veri', 'Kredi', 'Durum', 'Tarih & Saat'].map(h => (
                                                                        <th key={h} style={{ padding: '9px 12px', textAlign: 'left', fontSize: 10, fontWeight: 700, color: T.t3, textTransform: 'uppercase', letterSpacing: 0.7, borderBottom: `1px solid ${T.bd}` }}>{h}</th>
                                                                    ))}
                                                                </tr>
                                                            </thead>
                                                            <tbody>
                                                                {activityUser.recent_activities.slice(0, 30).map((a, i) => {
                                                                    const cfg = MODULE_LABELS[a.module];
                                                                    const meta = a.meta_data as Record<string, unknown> | undefined;
                                                                    const detailParts: string[] = [];
                                                                    if (meta?.query) detailParts.push(`🔍 "${String(meta.query).slice(0, 24)}"`);
                                                                    if (meta?.results_count !== undefined) detailParts.push(`${meta.results_count} sonuç`);
                                                                    if (meta?.country && String(meta.country).length > 0) detailParts.push(`🌍 ${meta.country}`);
                                                                    return (
                                                                        <tr key={a.id} style={{ borderBottom: i < activityUser.recent_activities.length - 1 ? `1px solid ${T.bd}22` : 'none' }}>
                                                                            <td style={{ padding: '9px 12px', whiteSpace: 'nowrap' }}>
                                                                                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, padding: '2px 8px', borderRadius: 6, background: `${cfg?.color || T.t3}15`, fontSize: 11, fontWeight: 600, color: cfg?.color || T.t3 }}>
                                                                                    {cfg?.icon} {cfg?.label || a.module}
                                                                                </span>
                                                                            </td>
                                                                            <td style={{ padding: '9px 12px', fontSize: 12, color: T.t1, maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={a.action}>{a.action}</td>
                                                                            <td style={{ padding: '9px 12px', fontSize: 11, color: T.t3, maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{detailParts.join(' · ')}</td>
                                                                            <td style={{ padding: '9px 12px', fontSize: 12, fontWeight: 700, color: a.credits_used > 0 ? T.gold : T.t3 }}>
                                                                                {a.credits_used > 0 ? `${a.credits_used}` : <span style={{ opacity: 0.3 }}>—</span>}
                                                                            </td>
                                                                            <td style={{ padding: '9px 12px' }}>
                                                                                <span style={{ fontSize: 10, padding: '2px 7px', borderRadius: 4, background: `${STATUS_COLORS[a.status] || T.t3}22`, color: STATUS_COLORS[a.status] || T.t3, fontWeight: 700 }}>
                                                                                    {a.status === 'success' ? '✓' : a.status === 'error' ? '✗' : '⏳'} {a.status}
                                                                                </span>
                                                                            </td>
                                                                            <td style={{ padding: '9px 12px', fontSize: 10, color: T.t3, whiteSpace: 'nowrap' }}>
                                                                                {a.created_at ? new Date(a.created_at).toLocaleString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—'}
                                                                            </td>
                                                                        </tr>
                                                                    );
                                                                })}
                                                            </tbody>
                                                        </table>
                                                        {activityUser.total_activities > 30 && (
                                                            <div style={{ textAlign: 'center', padding: '10px', fontSize: 11, color: T.t3, borderTop: `1px solid ${T.bd}` }}>
                                                                Son 30 kayıt gösteriliyor · Toplam <strong style={{ color: T.t1 }}>{activityUser.total_activities}</strong> aktivite
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            )}

                                            {activityUser.recent_activities.length === 0 && activityUser.module_summary.length === 0 && (
                                                <div style={{ textAlign: 'center', padding: '40px 20px', color: T.t3 }}>
                                                    <div style={{ fontSize: 40, marginBottom: 12 }}>📭</div>
                                                    <div style={{ fontSize: 14 }}>Bu kullanıcı henüz hiçbir modül kullanmamış.</div>
                                                    <div style={{ fontSize: 12, marginTop: 6, color: T.t3 }}>Aktiviteler otomatik olarak kaydedilmeye başlayacak.</div>
                                                </div>
                                            )}
                                        </>
                                    ) : null}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* ── API MANAGEMENT TAB ────────────────────────────── */}
                {tab === 'apis' && (
                    <div>
                        <div style={{ background: '#a78bfa11', border: '1px solid #a78bfa44', borderRadius: 12, padding: '12px 18px', marginBottom: 24, display: 'flex', gap: 10, alignItems: 'center' }}>
                            <span style={{ fontSize: 18 }}>🔐</span>
                            <div>
                                <div style={{ fontSize: 13, fontWeight: 600, color: '#a78bfa' }}>Güvenli Depolama</div>
                                <div style={{ fontSize: 12, color: T.t3 }}>API key&apos;ler Base64 ile şifrelenmiş olarak depolanır. Kopyala-yapıştır ile kolayca güncelleyin.</div>
                            </div>
                        </div>

                        {loading ? <LoadingSpinner /> : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                                {Object.entries(CAT_CONFIG).map(([cat, cfg]) => {
                                    const items = grouped[cat] || [];
                                    return (
                                        <div key={cat} style={{ background: T.bg2, border: `1px solid ${cfg.color}33`, borderRadius: 18, overflow: 'hidden' }}>
                                            <div style={{ padding: '18px 24px', background: `${cfg.color}0a`, borderBottom: `1px solid ${cfg.color}22`, display: 'flex', alignItems: 'center', gap: 12 }}>
                                                <div style={{ width: 36, height: 36, borderRadius: 10, background: `${cfg.color}22`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>{cfg.icon}</div>
                                                <div>
                                                    <div style={{ fontSize: 16, fontWeight: 700, color: cfg.color }}>{cfg.label}</div>
                                                    <div style={{ fontSize: 12, color: T.t3 }}>{cfg.desc}</div>
                                                </div>
                                                <div style={{ marginLeft: 'auto', fontSize: 12, color: T.t3 }}>
                                                    {items.filter(s => s.key_value).length}/{items.length} yapılandırıldı
                                                </div>
                                            </div>
                                            <div style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
                                                {items.map(s => (
                                                    <div key={s.key_name} style={{ background: T.bg3, borderRadius: 14, padding: '16px 20px', border: `1px solid ${T.bd}` }}>
                                                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
                                                            <div>
                                                                <div style={{ fontSize: 13, fontWeight: 700, color: T.t1, fontFamily: 'monospace', letterSpacing: 0.5 }}>{s.key_name}</div>
                                                                <div style={{ fontSize: 12, color: T.t3, marginTop: 3 }}>{s.description}</div>
                                                            </div>
                                                            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                                                                {s.is_sensitive && <span style={{ fontSize: 10, padding: '2px 7px', background: '#a78bfa22', color: '#a78bfa', borderRadius: 4 }}>🔒 Gizli</span>}
                                                                {s.key_value ? <span style={{ fontSize: 10, padding: '2px 7px', background: `${T.green}22`, color: T.green, borderRadius: 4 }}>✓ Ayarlı</span> : <span style={{ fontSize: 10, padding: '2px 7px', background: `${T.red}22`, color: T.red, borderRadius: 4 }}>✗ Boş</span>}
                                                            </div>
                                                        </div>
                                                        {s.key_value && (
                                                            <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 10, background: '#060b18', borderRadius: 8, padding: '8px 12px', border: `1px solid ${T.bd}` }}>
                                                                <span style={{ fontSize: 12, color: T.t3, flex: 1, fontFamily: 'monospace' }}>
                                                                    {showKey[s.key_name] ? s.key_value : '••••••••••••••••'}
                                                                </span>
                                                                <button onClick={() => setShowKey(p => ({ ...p, [s.key_name]: !p[s.key_name] }))} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 14, color: T.t3 }}>{showKey[s.key_name] ? '🙈' : '👁'}</button>
                                                            </div>
                                                        )}
                                                        <div style={{ display: 'flex', gap: 8 }}>
                                                            <input
                                                                type={s.is_sensitive && !showKey[s.key_name] ? 'password' : 'text'}
                                                                placeholder={s.key_value ? '▸ Yeni değer gir (değiştirmek için)' : '▸ Değer gir...'}
                                                                value={keyInputs[s.key_name] || ''}
                                                                onChange={e => setKeyInputs(p => ({ ...p, [s.key_name]: e.target.value }))}
                                                                style={{ ...inputStyle(T), flex: 1, marginBottom: 0 }}
                                                            />
                                                            <button onClick={() => saveSetting(s.key_name)} disabled={savingKey === s.key_name || !keyInputs[s.key_name]?.trim()}
                                                                style={{ padding: '9px 16px', background: T.goldD, border: `1px solid ${T.bdA}`, borderRadius: 10, color: T.gold, cursor: 'pointer', fontSize: 13, fontWeight: 600, opacity: !keyInputs[s.key_name]?.trim() ? 0.4 : 1, whiteSpace: 'nowrap' }}>
                                                                {savingKey === s.key_name ? '⏳' : '💾 Kaydet'}
                                                            </button>
                                                            {['GROQ_API_KEY', 'OPENAI_API_KEY', 'GOOGLE_MAPS_API_KEY', 'SENDGRID_API_KEY'].includes(s.key_name) && (
                                                                <button onClick={() => testSetting(s.key_name)} style={{ padding: '9px 14px', background: `${T.cyan}11`, border: `1px solid ${T.cyan}33`, borderRadius: 10, color: T.cyan, cursor: 'pointer', fontSize: 13, fontWeight: 600, whiteSpace: 'nowrap' }}>
                                                                    🧪 Test
                                                                </button>
                                                            )}
                                                        </div>
                                                        {testResults[s.key_name] && (
                                                            <div style={{ marginTop: 10, padding: '8px 12px', borderRadius: 8, fontSize: 12, background: testResults[s.key_name].status === 'success' ? `${T.green}11` : `${T.red}11`, color: testResults[s.key_name].status === 'success' ? T.green : T.red, border: `1px solid ${testResults[s.key_name].status === 'success' ? T.green : T.red}33` }}>
                                                                {testResults[s.key_name].message}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}

// ─── Helper Components ──────────────────────────────────────────
function LoadingSpinner() {
    return (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
            <div style={{ width: 36, height: 36, border: '3px solid #1a2844', borderTopColor: '#c9a227', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
        </div>
    );
}

function ActionBtn({ onClick, color, icon, title }: { onClick: () => void; color: string; icon: string; title?: string }) {
    return (
        <button onClick={onClick} title={title} style={{ width: 34, height: 34, display: 'flex', alignItems: 'center', justifyContent: 'center', background: `${color}11`, border: `1px solid ${color}33`, borderRadius: 8, cursor: 'pointer', fontSize: 14, transition: 'all 0.15s' }}>
            {icon}
        </button>
    );
}

function Modal({ title, children, onClose }: { title: string; children: React.ReactNode; onClose: () => void }) {
    return (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', zIndex: 999, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={e => e.target === e.currentTarget && onClose()}>
            <div style={{ background: '#0c1424', border: '1px solid rgba(201,162,39,0.2)', borderRadius: 20, padding: 28, width: 400, boxShadow: '0 24px 80px rgba(0,0,0,0.7)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                    <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: '#f1f5f9' }}>{title}</h3>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 18, cursor: 'pointer', color: '#475569' }}>✕</button>
                </div>
                {children}
            </div>
        </div>
    );
}

function inputStyle(T: Record<string, string>): React.CSSProperties {
    return { width: '100%', padding: '9px 14px', background: T.bg, border: `1px solid ${T.bd}`, borderRadius: 10, color: T.t1, fontSize: 14, outline: 'none', boxSizing: 'border-box', marginBottom: 0, fontFamily: "'Plus Jakarta Sans', sans-serif" };
}
