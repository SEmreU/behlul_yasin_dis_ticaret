# 🌍 TradeRadar - Dış Ticaret İstihbarat Yazılımı

> **AI destekli, çok modüllü dış ticaret istihbarat platformu**  
> Potansiyel müşteri bulma, ziyaretçi takibi, B2B platform taraması ve otomatik iletişim yönetimi

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📋 İçindekiler

- [Genel Bakış](#-genel-bakış)
- [Özellikler](#-özellikler)
- [Teknoloji Stack](#-teknoloji-stack)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Modüller](#-modüller)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Proje Yapısı](#-proje-yapısı)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

---

## 🎯 Genel Bakış

**TradeRadar**, dış ticaret yapan firmaların potansiyel müşteri bulma, pazar araştırması ve iletişim süreçlerini otomatikleştiren kapsamlı bir SaaS platformudur.

### Temel Sorunlar ve Çözümler

| Sorun | TradeRadar Çözümü |
|-------|-------------------|
| Web sitesi ziyaretçilerini tanıyamama | 🔭 **V-ID Modülü**: IP ve konum bazlı firma kimliklendirme |
| Manuel müşteri araştırması | 🤖 **AI Arama**: 7 dilde otomatik arama + görsel tanıma |
| Dağınık B2B platformlar | 🌐 **10 Platform Entegrasyonu**: Tek tıkla çoklu platform taraması |
| Yetkili kişiye ulaşamama | 📧 **Email Discovery**: Otomatik yetkili mail tespiti |
| Tekrarlayan email yazma | ✉️ **AI Kişiselleştirme**: GPT-4 ile otomatik email oluşturma |
| Fuar bilgisi eksikliği | 🎪 **Fuar İstihbaratı**: Global fuar takvimi ve katılımcı analizi |

---

## ✨ Özellikler

### 🔭 Modül 1: Ziyaretçi Kimliklendirme (V-ID)
- ✅ IP bazlı firma tespiti
- ✅ Geolocation API entegrasyonu
- ✅ Real-time bildirimler
- ✅ Excel export
- ✅ GDPR/KVKK uyumlu banner

### 🤖 Modül 2: AI Müşteri Bulma Botu
- ✅ 7 dilde arama (IATE + Cambridge sözlük doğrulaması)
- ✅ GPT-4 Vision ile görsel arama
- ✅ OEM No ve GTİP kodu desteği
- ✅ Çoklu arama motoru (Google, Yandex, Bing, Baidu)
- ✅ Dış ticaret veritabanları (TradeAtlas, ImportGenius, Panjiva)

### 🗺️ Modül 3: Harita ve Pazar Analizi
- ✅ Google Maps scraping
- ✅ Ülke/şehir bazlı firma bulma
- ✅ Geocoding servisi
- ✅ Excel export

### 🌐 Modül 4: 10 Küresel B2B Platform Entegrasyonu
**Desteklenen Platformlar:**
1. **Alibaba** (Çin & Global)
2. **Made-in-China** (Çin)
3. **DHgate** (Çin & Global)
4. **TradeKey** (Global - RFQ desteği)
5. **ECPlaza** (Güney Kore)
6. **eWorldTrade** (Global - RFQ desteği)
7. **IndiaMART** (Hindistan)
8. **TradeIndia** (Hindistan)
9. **EC21** (Global)
10. **Kompass** (Avrupa)
11. **Thomasnet** (Kuzey Amerika)

**Özellikler:**
- ✅ RFQ (Request for Quotation) tarama
- ✅ Çoklu platform aynı anda tarama
- ✅ Sonuçları Excel'e aktarma
- ✅ Yetkili mail vurgulama (purchasing@, manager@, etc.)

### 📧 Modül 5: İletişim Otomasyonu
- ✅ Email kampanya yönetimi
- ✅ GPT-4 ile AI kişiselleştirme
- ✅ Chatbot servisi
- ✅ Template yönetimi

### 🎪 Modül 6: Fuar İstihbaratı ve CRM
- ✅ Global fuar takvimi
- ✅ Salesforce entegrasyonu
- ✅ HubSpot entegrasyonu
- ✅ Subscription yönetimi

---

## 🛠️ Teknoloji Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **AI/ML**: OpenAI GPT-4, GPT-4 Vision
- **Scraping**: BeautifulSoup4, Selenium, Playwright
- **Task Queue**: Celery + Redis
- **API Clients**: httpx, requests

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS (custom dark theme)
- **State Management**: React Hooks
- **HTTP Client**: Fetch API
- **UI Components**: Custom component library

### DevOps & Tools
- **Containerization**: Docker + Docker Compose
- **API Documentation**: Swagger/OpenAPI
- **Version Control**: Git
- **Package Manager**: npm (frontend), pip (backend)

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker (opsiyonel)

### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/yourusername/traderadar.git
cd traderadar
```

### 2. Backend Kurulumu

```bash
# Backend dizinine gidin
cd backend

# Virtual environment oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# .env dosyasını oluşturun
cp .env.example .env
# .env dosyasını düzenleyin (API anahtarları, database URL, vb.)

# Database migration
alembic upgrade head

# Backend'i başlatın
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Kurulumu

```bash
# Frontend dizinine gidin
cd frontend

# Bağımlılıkları yükleyin
npm install

# .env.local dosyasını oluşturun
cp .env.example .env.local
# .env.local dosyasını düzenleyin

# Development server'ı başlatın
npm run dev
```

### 4. Docker ile Kurulum (Alternatif)

```bash
# Tüm servisleri başlatın
docker-compose up -d

# Logları görüntüleyin
docker-compose logs -f
```

**Servisler:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## 📖 Kullanım

### 1. Kullanıcı Kaydı ve Giriş

```bash
# Frontend'e gidin
http://localhost:3000

# Kayıt olun
Email: demo@example.com
Password: ********

# Giriş yapın
```

### 2. Ziyaretçi Takibi

```bash
# Dashboard > Ziyaretçi Takibi
- Gerçek zamanlı ziyaretçi listesi
- Excel export butonu
- GDPR banner (ilk ziyaret)
```

### 3. B2B Platform Tarama

```bash
# Dashboard > B2B Platformlar
1. Platform seçin (örn: TradeKey, IndiaMART, Alibaba)
2. Arama terimi girin (örn: "automotive parts")
3. "Platformları Tara" butonuna tıklayın
4. Sonuçları görüntüleyin
5. "Excel İndir" ile kaydedin
```

### 4. RFQ Tarama

```bash
# Dashboard > B2B Platformlar > RFQ Tarama sekmesi
1. RFQ arama terimi girin
2. Platform seçin
3. Sonuçları görüntüleyin
4. Excel'e aktarın
```

### 5. Harita Araştırma

```bash
# Dashboard > Harita Araştırma
1. Ülke seçin (örn: Almanya)
2. Anahtar kelimeler girin (örn: "automotive", "spare parts")
3. "Haritada Ara" butonuna tıklayın
4. "Excel İndir" ile sonuçları kaydedin
```

---

## 📦 Modüller

### Modül Detayları

#### 1. Ziyaretçi Kimliklendirme (V-ID)
**Dosyalar:**
- `backend/app/services/visitor_tracking.py`
- `backend/app/api/endpoints/visitor.py`
- `frontend/app/[locale]/dashboard/visitors/page.tsx`

**API Endpoints:**
```
GET  /api/v1/visitor/visitors?limit=100
POST /api/v1/visitor/track
GET  /api/v1/visitor/export
```

#### 2. B2B Platform Tarama
**Dosyalar:**
- `backend/app/services/b2b_scraper.py`
- `backend/app/services/marketplace_scrapers.py`
- `backend/app/api/endpoints/marketplace.py`
- `frontend/app/[locale]/dashboard/b2b/page.tsx`

**API Endpoints:**
```
POST /api/v1/marketplace/search-all
POST /api/v1/marketplace/search-rfqs
GET  /api/v1/marketplace/export
GET  /api/v1/marketplace/export-rfqs
```

#### 3. Excel Export Servisi
**Dosyalar:**
- `backend/app/services/excel_export.py`
- `frontend/lib/api-helpers.ts`
- `frontend/components/ExcelExportButton.tsx`

**Fonksiyonlar:**
```python
# Backend
ExcelExportService.export_visitors()
ExcelExportService.export_marketplace_results()
ExcelExportService.export_rfqs()
ExcelExportService.export_map_results()
```

```typescript
// Frontend
exportVisitorsToExcel(limit)
exportMarketplaceToExcel(query, platforms)
exportRFQsToExcel(query, country)
exportMapsToExcel(country, keywords, city)
```

---

## 📚 API Dokümantasyonu

### Swagger UI
Backend çalıştıktan sonra:
```
http://localhost:8000/docs
```

### Örnek API Çağrıları

#### Ziyaretçi Listesi
```bash
curl -X GET "http://localhost:8000/api/v1/visitor/visitors?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### B2B Arama
```bash
curl -X POST "http://localhost:8000/api/v1/marketplace/search-all" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "automotive parts",
    "platforms": ["alibaba", "tradekey", "indiamart"],
    "search_type": "product"
  }'
```

#### Excel Export
```bash
curl -X GET "http://localhost:8000/api/v1/visitor/export?limit=1000" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o visitors.xlsx
```

---

## 📁 Proje Yapısı

```
traderadar/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       ├── visitor.py
│   │   │       ├── marketplace.py
│   │   │       ├── maps.py
│   │   │       └── b2b.py
│   │   ├── services/
│   │   │   ├── visitor_tracking.py
│   │   │   ├── b2b_scraper.py
│   │   │   ├── marketplace_scrapers.py
│   │   │   ├── excel_export.py
│   │   │   └── crm_integration.py
│   │   ├── models/
│   │   ├── core/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   └── [locale]/
│   │       ├── dashboard/
│   │       │   ├── visitors/page.tsx
│   │       │   ├── b2b/page.tsx
│   │       │   ├── maps/page.tsx
│   │       │   └── search/page.tsx
│   │       └── login/page.tsx
│   ├── components/
│   │   ├── GDPRBanner.tsx
│   │   ├── ExcelExportButton.tsx
│   │   └── dashboard/
│   │       └── DashboardLayout.tsx
│   ├── lib/
│   │   └── api-helpers.ts
│   ├── package.json
│   └── .env.example
│
├── docker-compose.yml
├── README.md
├── SETUP.md
└── API_KEYS.md
```

---

## 🎨 Frontend Özellikleri

### GDPR/KVKK Banner
- İlk ziyarette otomatik gösterim
- LocalStorage ile kullanıcı tercihini kaydetme
- Detaylı bilgi gösterme/gizleme
- Kabul/Reddet butonları

### Excel Export Button
- Reusable component
- Loading state desteği
- Disabled state desteği
- Mevcut tasarım sistemi ile uyumlu

### Yetkili Mail Vurgulama
Otomatik olarak tespit edilen yetkili mailler:
- `purchasing@` - Satın alma
- `procurement@` - Tedarik
- `manager@` - Yönetici
- `sales@` - Satış
- `director@` - Direktör
- `ceo@`, `cto@`, `cfo@` - Üst yönetim
- `export@`, `import@` - Dış ticaret

**Görsel Vurgulama:**
- 📧 ikonu
- Hafif yeşil arka plan (`bg-[#00e5a008]`)
- Hover'da "Yetkili Mail" tooltip

---

## 🔐 Güvenlik

### Kimlik Doğrulama
- JWT (JSON Web Tokens)
- Access token + Refresh token
- Token expiration: 30 dakika (access), 7 gün (refresh)

### GDPR/KVKK Uyumluluğu
- Kullanıcı onayı (GDPR banner)
- Veri saklama süresi: 2 yıl
- Veri silme hakkı
- Veri erişim hakkı

### API Güvenliği
- Rate limiting
- CORS yapılandırması
- SQL injection koruması (SQLAlchemy ORM)
- XSS koruması

---

## 🧪 Test

### Backend Testleri
```bash
cd backend
pytest tests/ -v
```

### Frontend Testleri
```bash
cd frontend
npm run test
```

### E2E Testleri
```bash
npm run test:e2e
```

---

## 📊 Performans

### Optimizasyonlar
- Database indexing (IP, email, company)
- Redis caching (API responses)
- Lazy loading (frontend)
- Image optimization (Next.js)
- Code splitting (React)

### Benchmark
- API response time: < 200ms (ortalama)
- Excel export: ~1000 kayıt/saniye
- Concurrent users: 100+
- Database queries: < 50ms

---

## 🔄 Gelecek Özellikler

### Planlanan Geliştirmeler
- [ ] WebSocket ile real-time notifications
- [ ] Google Maps widget entegrasyonu
- [ ] Chatbot embed widget
- [ ] Email template editor
- [ ] Advanced filtering ve sorting
- [ ] Multi-language support (EN, DE, FR, ES)
- [ ] Mobile app (React Native)
- [ ] AI-powered lead scoring
- [ ] Automated follow-up emails
- [ ] Integration with more CRMs (Zoho, Pipedrive)

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

### Kod Standartları
- **Python**: PEP 8, type hints kullanın
- **TypeScript**: ESLint + Prettier
- **Commit Messages**: Conventional Commits formatı

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👥 Ekip

- **Backend Development**: FastAPI, PostgreSQL, AI/ML
- **Frontend Development**: Next.js, TypeScript, Tailwind CSS
- **DevOps**: Docker, CI/CD
- **UI/UX Design**: Figma, Custom Design System

---

## 📞 İletişim

- **Email**: support@traderadar.com
- **Website**: https://traderadar.com
- **Documentation**: https://docs.traderadar.com

---

## 🙏 Teşekkürler

Bu proje aşağıdaki açık kaynak projeleri kullanmaktadır:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [OpenAI](https://openai.com/)
- [Tailwind CSS](https://tailwindcss.com/)

---

## 📈 Proje Durumu

### Son Güncelleme: 14 Şubat 2026

**Tamamlanan Modüller:**
- ✅ Ziyaretçi Kimliklendirme (V-ID)
- ✅ AI Müşteri Bulma Botu
- ✅ Harita ve Pazar Analizi
- ✅ 10 B2B Platform Entegrasyonu
- ✅ İletişim Otomasyonu
- ✅ Fuar İstihbaratı ve CRM

**Frontend Entegrasyonu:**
- ✅ GDPR/KVKK Banner
- ✅ Excel Export Buttons
- ✅ API Integration
- ✅ Authority Email Highlighting
- ✅ RFQ Support
- ✅ 10 Platform UI

**Backend Servisleri:**
- ✅ Universal Excel Export
- ✅ 8 Yeni Marketplace Scraper
- ✅ Salesforce/HubSpot CRM Integration
- ✅ RFQ Scraping

---

## 📖 Ek Dokümantasyon

- [SETUP.md](SETUP.md) - Detaylı kurulum talimatları
- [API_KEYS.md](API_KEYS.md) - API anahtarları yapılandırması
- [WALKTHROUGH.md](WALKTHROUGH.md) - Özellik walkthrough
- [TASK.md](TASK.md) - Geliştirme task listesi

---

<div align="center">

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

Made with ❤️ by TradeRadar Team

</div>
