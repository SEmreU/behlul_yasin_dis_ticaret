'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useParams } from 'next/navigation';

const MODULES = [
    { id: "dashboard", icon: "◉", label: "Dashboard", desc: "Genel Bakış", href: "/dashboard" },
    { id: "visitors", icon: "👁", label: "Ziyaretçi Takibi", desc: "Modül 1", href: "/dashboard/visitors" },
    { id: "search", icon: "🔍", label: "Müşteri Arama", desc: "Modül 2", href: "/dashboard/search" },
    { id: "maps", icon: "🗺", label: "Harita Araştırma", desc: "Modül 3", href: "/dashboard/maps" },
    { id: "b2b", icon: "🌐", label: "B2B Platformlar", desc: "Ek Modül", href: "/dashboard/b2b" },
    { id: "contact", icon: "📧", label: "İletişim Bulucu", desc: "Modül 4", href: "/dashboard/contact" },
    { id: "automail", icon: "✉", label: "Otomatik Mail", desc: "Modül 5", href: "/dashboard/automail" },
    { id: "chatbot", icon: "🤖", label: "AI Chatbot", desc: "Modül 6", href: "/dashboard/chatbot" },
    { id: "fairs", icon: "🎪", label: "Fuar Analizi", desc: "Modül 7", href: "/dashboard/fairs" },
    { id: "china", icon: "🇨🇳", label: "Çin Pazarı", desc: "Modül 8", href: "/dashboard/china" },
    { id: "usa", icon: "🇺🇸", label: "ABD Pazarı", desc: "Modül 9", href: "/dashboard/usa" },
    { id: "pricing", icon: "💎", label: "Fiyatlandırma", desc: "Paketler", href: "/dashboard/pricing" },
    { id: "admin", icon: "⚙️", label: "Admin Paneli", desc: "Yönetim", href: "/dashboard/admin" },
];

const T = {
    bg: "#060b18", bg2: "#0c1424", bg3: "#111c32", bg4: "#1a2844",
    gold: "#c9a227", goldL: "#e8c84a", goldD: "rgba(201,162,39,0.12)", goldG: "rgba(201,162,39,0.25)",
    cyan: "#22d3ee", green: "#34d399", violet: "#a78bfa",
    t1: "#f1f5f9", t2: "#94a3b8", t3: "#475569",
    bd: "rgba(255,255,255,0.06)", bdA: "rgba(201,162,39,0.2)",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const [collapsed, setCollapsed] = useState(false);
    const pathname = usePathname();
    const params = useParams();
    const locale = params?.locale || 'tr';

    // Ziyaretçi takip — sayfa yüklendiğinde bir kez çalışır
    useEffect(() => {
        const sessionKey = 'vt_session_id';
        let sid = sessionStorage.getItem(sessionKey);
        if (!sid) {
            sid = Math.random().toString(36).slice(2) + Date.now();
            sessionStorage.setItem(sessionKey, sid);
        }
        const API = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1/visitor/track';
        const doTrack = (lat: number | null, lng: number | null, granted: boolean) => {
            fetch(API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sid, latitude: lat, longitude: lng, location_permission_granted: granted }),
            }).catch(() => { });
        };
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (p) => doTrack(p.coords.latitude, p.coords.longitude, true),
                () => doTrack(null, null, false),
                { timeout: 5000 }
            );
        } else {
            doTrack(null, null, false);
        }
    }, []);

    // Get current path without locale
    const currentPath = pathname?.replace(/^\/[a-z]{2}/, '') || '/dashboard';

    return (
        <div style={{ minHeight: "100vh", background: T.bg, fontFamily: "'Plus Jakarta Sans',sans-serif", color: T.t1, display: "flex" }}>
            <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
            <style>{`
        *{margin:0;padding:0;box-sizing:border-box}
        body{margin:0;background:${T.bg};overflow-x:hidden}
        ::-webkit-scrollbar{width:6px}
        ::-webkit-scrollbar-track{background:transparent}
        ::-webkit-scrollbar-thumb{background:${T.bg4};border-radius:3px}
        ::-webkit-scrollbar-thumb:hover{background:${T.gold}}
        input:focus,select:focus,textarea:focus{border-color:${T.gold}66!important}
        button:hover{filter:brightness(1.08)}
        ::placeholder{color:${T.t3}}
        select option{background:${T.bg};color:${T.t1}}
      `}</style>

            {/* SIDEBAR */}
            <aside style={{
                position: "fixed", top: 0, left: 0, height: "100vh", width: collapsed ? 72 : 260,
                background: `linear-gradient(180deg, ${T.bg2}, ${T.bg3})`,
                borderRight: `1px solid ${T.bdA}22`, display: "flex", flexDirection: "column",
                transition: "width 0.3s ease", zIndex: 100, overflowY: "auto", overflowX: "hidden",
            }}>
                <div style={{ padding: "20px 16px", display: "flex", alignItems: "center", gap: 12, borderBottom: `1px solid ${T.bd}`, minHeight: 72 }}>
                    <div style={{
                        width: 36, height: 36, background: `linear-gradient(135deg, ${T.gold}, ${T.goldL})`,
                        borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 16, fontWeight: 800, color: T.bg, flexShrink: 0,
                        fontFamily: "'Playfair Display',serif", boxShadow: `0 0 16px ${T.goldG}`,
                    }}>Y</div>
                    {!collapsed && <div>
                        <div style={{ fontSize: 16, fontWeight: 700, color: T.t1, whiteSpace: "nowrap" }}>Yasin <span style={{ color: T.gold }}>DT</span></div>
                        <div style={{ fontSize: 10, color: T.t3, letterSpacing: 1.5, whiteSpace: "nowrap", textTransform: "uppercase" }}>İstihbarat Platformu</div>
                    </div>}
                </div>

                <nav style={{ flex: 1, padding: "8px 0" }}>
                    {MODULES.map(m => {
                        const isActive = currentPath === m.href || (m.href === '/dashboard' && currentPath === '/dashboard');
                        const localizedHref = `/${locale}${m.href}`;
                        return (
                            <Link key={m.id} href={localizedHref} style={{
                                width: "100%", display: "flex", alignItems: "center", gap: 12, padding: "10px 16px",
                                border: "none", cursor: "pointer", transition: "all 0.2s", textAlign: "left", fontSize: 14, textDecoration: "none",
                                background: isActive ? T.goldD : "transparent",
                                borderLeft: `3px solid ${isActive ? T.gold : "transparent"}`,
                                color: isActive ? T.gold : T.t3,
                            }}>
                                <span style={{ fontSize: 18, flexShrink: 0, width: 28, textAlign: "center" }}>{m.icon}</span>
                                {!collapsed && <div>
                                    <div style={{ fontWeight: isActive ? 600 : 500, whiteSpace: "nowrap" }}>{m.label}</div>
                                    <div style={{ fontSize: 11, opacity: 0.5, whiteSpace: "nowrap" }}>{m.desc}</div>
                                </div>}
                            </Link>
                        );
                    })}
                </nav>

                <button onClick={() => setCollapsed(!collapsed)} style={{
                    margin: "8px 16px 16px", padding: 8, background: `${T.gold}11`, border: `1px solid ${T.bdA}`,
                    borderRadius: 8, color: T.gold, cursor: "pointer", fontSize: 14,
                }}>{collapsed ? "▸" : "◂"}</button>
            </aside>

            {/* MAIN */}
            <main style={{ flex: 1, marginLeft: collapsed ? 72 : 260, transition: "margin-left 0.3s ease", minHeight: "100vh", display: "flex", flexDirection: "column" }}>
                <header style={{
                    height: 64, borderBottom: `1px solid ${T.bd}`, display: "flex", alignItems: "center", justifyContent: "space-between",
                    padding: "0 28px", background: `${T.bg2}88`, backdropFilter: "blur(10px)", position: "sticky", top: 0, zIndex: 50,
                }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, background: T.bg3, border: `1px solid ${T.bd}`, borderRadius: 10, padding: "8px 16px", width: 320 }}>
                        <span style={{ opacity: 0.4 }}>🔍</span>
                        <input placeholder="Modül veya özellik ara..." style={{ background: "transparent", border: "none", color: T.t2, fontSize: 14, outline: "none", fontFamily: "inherit", flex: 1 }} />
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        {["🔔", "⚙️"].map((ic, i) => (
                            <button key={i} style={{ width: 38, height: 38, display: "flex", alignItems: "center", justifyContent: "center", background: T.bg3, border: `1px solid ${T.bd}`, borderRadius: 10, cursor: "pointer", fontSize: 16 }}>{ic}</button>
                        ))}
                        <div style={{
                            width: 38, height: 38, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center",
                            background: `linear-gradient(135deg, ${T.gold}, ${T.goldL})`, fontSize: 13, fontWeight: 800, color: T.bg, marginLeft: 4,
                        }}>YD</div>
                    </div>
                </header>
                <div style={{ flex: 1, overflowY: "auto" }}>{children}</div>
            </main>
        </div>
    );
}
