'use client';

import DashboardLayout from '@/components/dashboard/DashboardLayout';

const DB_SOURCES = [
  'TradeAtlas', 'ImportGenius', 'Trademo Intel', 'Panjiva', 'Global Buyers Online',
  'Europages', 'TradeKey', 'TradeMap', 'OneWorld Yellow Pages', 'Vujis',
  'Apify', 'Exim Data', 'TradeCalculusAI', 'UN Comtrade'
];

export default function DashboardPage() {
  const stats = [
    { label: 'Toplam Sorgu', value: '12,847', change: '+18%', icon: '🔍', color: '#00e5a0' },
    { label: 'Bulunan Müşteri', value: '3,291', change: '+24%', icon: '👥', color: '#0ea5e9' },
    { label: 'Gönderilen Mail', value: '8,450', change: '+12%', icon: '✉️', color: '#a855f7' },
    { label: 'Aktif Ülke', value: '47', change: '+3', icon: '🌍', color: '#f59e0b' },
  ];

  const recentActivity = [
    { type: 'visitor', text: "Almanya'dan Bosch GmbH ziyaret etti", time: '2 dk önce' },
    { type: 'search', text: "İngiltere - 'automotive spare parts' araması tamamlandı", time: '15 dk önce' },
    { type: 'mail', text: '47 firmaya otomatik tanıtım maili gönderildi', time: '1 saat önce' },
    { type: 'map', text: 'Fransa harita araması - 23 firma bulundu', time: '2 saat önce' },
    { type: 'fair', text: 'Automechanika Dubai katılımcı listesi analiz edildi', time: '3 saat önce' },
  ];

  return (
    <DashboardLayout>
      <div className="p-8 pb-12">
        {/* Page Header */}
        <div className="mb-7">
          <h2 className="text-[26px] font-bold m-0 text-[#e2e8f0]">Dashboard</h2>
          <p className="text-[15px] text-[#64748b] mt-2">
            Dış ticaret istihbarat aktivitelerinizin genel görünümü
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-7">
          {stats.map((s, i) => (
            <div
              key={i}
              className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl p-5 relative overflow-hidden"
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div className="flex justify-between items-center mb-3">
                <span className="text-[22px]">{s.icon}</span>
                <span className="text-[13px] font-semibold" style={{ color: s.color }}>
                  {s.change}
                </span>
              </div>
              <div className="text-[32px] font-bold text-[#e2e8f0] tracking-tight mb-1">
                {s.value}
              </div>
              <div className="text-[13px] text-[#64748b]">{s.label}</div>
              <div
                className="absolute bottom-0 left-0 right-0 h-[3px]"
                style={{ background: `linear-gradient(90deg, ${s.color}44, ${s.color})` }}
              />
            </div>
          ))}
        </div>

        {/* Dashboard Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Recent Activity */}
          <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl p-6">
            <h3 className="text-base font-semibold text-[#e2e8f0] m-0 mb-5">
              Son Aktiviteler
            </h3>
            {recentActivity.map((a, i) => (
              <div
                key={i}
                className="flex items-start gap-3 py-3 border-b border-[#1e3a5f22] last:border-0"
              >
                <div className="w-2 h-2 rounded-full bg-[#00e5a0] mt-1.5 flex-shrink-0" />
                <div className="flex-1">
                  <div className="text-sm text-[#cbd5e1]">{a.text}</div>
                  <div className="text-xs text-[#475569] mt-0.5">{a.time}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Data Sources */}
          <div className="bg-gradient-to-br from-[#0d1f35] to-[#0a1628] border border-[#1e3a5f44] rounded-2xl p-6">
            <h3 className="text-base font-semibold text-[#e2e8f0] m-0 mb-5">
              Veri Kaynakları
            </h3>
            <div className="flex flex-wrap gap-2">
              {DB_SOURCES.map((s, i) => (
                <div
                  key={i}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0a1628] border border-[#1e3a5f44] rounded-lg text-[13px] text-[#94a3b8]"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-[#00e5a0]" />
                  {s}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
