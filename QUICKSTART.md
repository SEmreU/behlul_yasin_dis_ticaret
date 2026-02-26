# 🚀 Yasin Dış Ticaret - Çalıştırma Klavuzu

**Son Güncelleme:** 2026-02-06
**Versiyon:** 2026.1

---

## 📋 Sistem Gereksinimleri

### Zorunlu
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Disk Alanı**: Minimum 5GB boş alan

### Opsiyonel (Local Development için)
- **Node.js**: 20.x veya üzeri
- **Python**: 3.12+
- **PostgreSQL**: 16+ (Docker kullanmıyorsanız)

---

## 🎯 Hızlı Başlangıç (3 Adım)

### 1️⃣ Environment Dosyasını Hazırla

```bash
cd /home/behlul/yasin-dis-ticaret/backend

# .env dosyası zaten var, isteğe bağlı düzenle
nano .env
```

**Önemli API Keys (Opsiyonel):**
```env
# OpenAI (Ürün arama, AI özellikler için)
OPENAI_API_KEY=sk-your-key-here

# Google Maps (Scraping için)
GOOGLE_MAPS_API_KEY=your-google-key

# SendGrid (Email kampanyaları için)
SENDGRID_API_KEY=SG.your-key-here
```

### 2️⃣ Docker ile Tüm Servisleri Başlat

```bash
cd /home/behlul/yasin-dis-ticaret

# Tüm servisleri başlat (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# Logları izle (opsiyonel)
docker-compose logs -f
```

**Beklenen Çıktı:**
```
✅ yasin-trade-postgres   - Started
✅ yasin-trade-redis      - Started
✅ yasin-trade-backend    - Started
✅ yasin-trade-frontend   - Started
```

### 3️⃣ Database Migration Çalıştır

```bash
# Backend container'ına gir
docker-compose exec backend bash

# Migration'ları çalıştır
alembic upgrade head

# Çık
exit
```

---

## 🌐 Erişim URL'leri

| Servis | URL | Açıklama |
|--------|-----|----------|
| **Frontend** | http://localhost:3000 | Ana uygulama |
| **Backend API** | http://localhost:8000 | REST API |
| **API Dokümanı** | http://localhost:8000/docs | Swagger UI |
| **Alternative Docs** | http://localhost:8000/redoc | ReDoc UI |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache |

---

## 👤 İlk Kullanıcı Oluşturma

### Yöntem 1: API ile (Önerilen)

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yasin.com",
    "password": "admin12345",
    "full_name": "Yasin Admin"
  }'
```

**Beklenen Yanıt:**
```json
{
  "id": 1,
  "email": "admin@yasin.com",
  "full_name": "Yasin Admin",
  "is_active": true,
  "subscription_tier": "free"
}
```

### Yöntem 2: Frontend ile

1. Tarayıcıda http://localhost:3000/tr/register aç
2. Email, şifre ve ad bilgilerini gir
3. "Kayıt Ol" butonuna tıkla
4. http://localhost:3000/tr/login sayfasından giriş yap

---

## 🔐 Giriş Yapma ve Token Alma

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@yasin.com",
    "password": "admin12345"
  }'
```

**Yanıt:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token ile API Kullanımı:**
```bash
TOKEN="your-access-token-here"

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📱 Frontend Sayfaları

### Ana Sayfalar

| Sayfa | URL | Açıklama |
|-------|-----|----------|
| Ana Sayfa | http://localhost:3000/tr | Landing page |
| Giriş | http://localhost:3000/tr/login | Login |
| Kayıt | http://localhost:3000/tr/register | Signup |
| Dashboard | http://localhost:3000/tr/dashboard | Ana panel |
| Ürün Arama | http://localhost:3000/tr/search | 8 dilde arama |
| Kampanyalar | http://localhost:3000/tr/campaigns | Email kampanyaları |
| Analytics | http://localhost:3000/tr/analytics | İstatistikler |

### Dil Değiştirme

Platform 8 dilde çalışır. URL'deki locale'i değiştirin:
- 🇹🇷 Türkçe: `/tr/dashboard`
- 🇬🇧 English: `/en/dashboard`
- 🇪🇸 Español: `/es/dashboard`
- 🇷🇺 Русский: `/ru/dashboard`
- 🇸🇦 العربية: `/ar/dashboard`
- 🇫🇷 Français: `/fr/dashboard`
- 🇩🇪 Deutsch: `/de/dashboard`
- 🇨🇳 中文: `/zh/dashboard`

---

## 🔧 API Endpoint'leri

### 🔐 Authentication

```bash
# Kayıt ol
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}

# Giriş yap
POST /api/v1/auth/login/json
{
  "username": "user@example.com",
  "password": "password123"
}

# Profil bilgisi
GET /api/v1/auth/me
Header: Authorization: Bearer {token}
```

### 🔍 Ürün Arama (8 Dil)

```bash
# Ürün ara
POST /api/v1/search/product
{
  "query": "hydraulic pump",
  "language": "en",
  "search_type": "general"
}

# Görsel ile ara
POST /api/v1/search/image-search
{
  "image_url": "https://example.com/product.jpg"
}

# Çeviri
POST /api/v1/search/translate
{
  "text": "hidrolik pompa",
  "source_lang": "tr",
  "target_lang": "en"
}
```

### 👥 Ziyaretçi Tracking

```bash
# Ziyaretçi kaydet
POST /api/v1/visitor/track
{
  "ip_address": "185.123.45.67",
  "page_url": "/products/hydraulic-pump",
  "user_agent": "Mozilla/5.0..."
}

# Ziyaretçileri listele
GET /api/v1/visitor/visitors?skip=0&limit=50
```

### 🗺️ Google Maps Scraping

```bash
# Firma topla
POST /api/v1/scraping/google-maps
{
  "query": "hydraulic pump manufacturer istanbul",
  "max_results": 50
}

# Sonuçları listele
GET /api/v1/scraping/results
```

### 📧 Email Kampanyaları

```bash
# Kampanya oluştur
POST /api/v1/campaigns/create
{
  "name": "Spring 2026 Campaign",
  "subject": "New Hydraulic Pumps",
  "body": "Dear {name}, check our new products...",
  "company_ids": [1, 2, 3, 4]
}

# Kampanyayı gönder
POST /api/v1/campaigns/{campaign_id}/send

# Kampanyaları listele
GET /api/v1/campaigns/
```

### 📊 Analytics

```bash
# Dashboard istatistikleri
GET /api/v1/analytics/dashboard

# Firmaları Excel'e aktar
GET /api/v1/analytics/export/companies
```

### 🛡️ GDPR/KVKK

```bash
# Verilerimi indir
GET /api/v1/gdpr/my-data

# Hesabı sil
DELETE /api/v1/gdpr/delete-account
```

### 💳 Subscription

```bash
# Planları gör
GET /api/v1/subscription/plans

# Upgrade yap
POST /api/v1/subscription/upgrade
{
  "plan": "pro"
}

# Kullanım limitlerini kontrol et
GET /api/v1/subscription/usage
```

---

## 🧪 Test Etme

### Backend Testleri

```bash
# Backend container'ına gir
docker-compose exec backend bash

# Tüm testleri çalıştır
pytest tests/ -v

# Sadece bir modülü test et
pytest tests/test_auth.py -v

# Coverage ile
pytest tests/ --cov=app --cov-report=html
```

### Frontend Testleri

```bash
# Frontend container'ına gir (local development gerekir)
cd frontend
npm test

# E2E testler
npm run test:e2e
```

---

## 🐛 Sorun Giderme

### Problem 1: Docker servisleri başlamıyor

```bash
# Tüm container'ları durdur
docker-compose down

# Volume'ları temizle
docker-compose down -v

# Yeniden başlat
docker-compose up -d --build
```

### Problem 2: Database connection error

```bash
# PostgreSQL çalışıyor mu kontrol et
docker ps | grep postgres

# Logları incele
docker-compose logs postgres

# Manuel bağlantı testi
docker-compose exec postgres psql -U yasin -d yasin_trade_db -c "SELECT 1;"
```

### Problem 3: Migration hatası

```bash
# Container'a gir
docker-compose exec backend bash

# Migration'ları sıfırla
alembic downgrade base

# Yeniden çalıştır
alembic upgrade head
```

### Problem 4: Frontend başlamıyor

```bash
# Frontend container'ını yeniden build et
docker-compose build frontend
docker-compose up -d frontend

# Logları kontrol et
docker-compose logs frontend
```

### Problem 5: Port already in use

```bash
# Kullanılan portları kontrol et
sudo lsof -i :3000  # Frontend
sudo lsof -i :8000  # Backend
sudo lsof -i :5432  # PostgreSQL

# İlgili process'i durdur
kill -9 <PID>

# Veya docker-compose.yml'deki portları değiştir
```

### Problem 6: Playwright hatası

```bash
# Backend container'ını yeniden build et (Dockerfile güncellemesi yapıldı)
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

## 🔄 Container Yönetimi

### Servisleri Yönetme

```bash
# Tüm servisleri başlat
docker-compose up -d

# Sadece backend'i başlat
docker-compose up -d backend

# Logları izle
docker-compose logs -f backend

# Container'a gir
docker-compose exec backend bash
docker-compose exec frontend sh

# Servisleri durdur
docker-compose stop

# Servisleri tamamen kaldır
docker-compose down

# Volume'larla birlikte kaldır (dikkat: veriler silinir!)
docker-compose down -v
```

### Database İşlemleri

```bash
# PostgreSQL'e bağlan
docker-compose exec postgres psql -U yasin -d yasin_trade_db

# Backup al
docker-compose exec postgres pg_dump -U yasin yasin_trade_db > backup.sql

# Restore et
docker-compose exec -T postgres psql -U yasin yasin_trade_db < backup.sql
```

---

## 🛠️ Local Development (Docker'sız)

### Backend (Python)

```bash
cd backend

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# PostgreSQL ve Redis'i Docker ile başlat
docker-compose up -d postgres redis

# Backend'i çalıştır
uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd frontend

# Bağımlılıkları yükle
npm install

# Development server'ı başlat
npm run dev

# Production build
npm run build
npm start
```

---

## 📊 Proje Özeti

| Özellik | Durum | Açıklama |
|---------|-------|----------|
| **Backend API** | ✅ | FastAPI + Python 3.12 |
| **Frontend** | ✅ | Next.js 15 + TypeScript |
| **Database** | ✅ | PostgreSQL 16 |
| **Cache** | ✅ | Redis 7 |
| **Containerization** | ✅ | Docker + Docker Compose |
| **API Endpoints** | ✅ | 40+ endpoint |
| **Çoklu Dil** | ✅ | 8 dil desteği |
| **Authentication** | ✅ | JWT tokens |
| **GDPR/KVKK** | ✅ | Veri yönetimi |

### Modüller

| # | Modül | Durum |
|---|-------|-------|
| 1 | Ziyaretçi Kimliklendirme | ✅ |
| 2 | Akıllı Ürün Arama (8 Dil) | ✅ |
| 3 | Google Maps Scraping | ✅ |
| 4 | Email Kampanyaları | ✅ |
| 5 | Fuar Analizi | ✅ |
| 6 | Analytics & Raporlama | ✅ |
| 7 | GDPR/KVKK Uyumluluk | ✅ |
| 8 | Subscription Yönetimi | ✅ |

---

## 🎯 Sonraki Adımlar

### Geliştirme İçin
1. ✅ API keys ekle (.env dosyası)
2. ✅ Frontend'i özelleştir
3. ✅ Test senaryoları ekle
4. ✅ Email template'lerini düzenle

### Production İçin
1. 📝 Domain hazırla
2. 📝 SSL sertifikası al
3. 📝 Railway/Vercel'e deploy et
4. 📝 Environment variables'ları production'a aktar
5. 📝 Monitoring ekle (Sentry, LogRocket)

---

## 📚 Ek Dokümantasyon

- **README.md**: Genel proje bilgisi ve mimari
- **DEPLOYMENT.md**: Production deployment klavuzu
- **DATABASE_SCHEMA.md**: Veritabanı şeması detayları
- **API Docs**: http://localhost:8000/docs (Swagger UI)

---

## 💡 Faydalı Komutlar

```bash
# Sistem kaynaklarını izle
docker stats

# Tüm container'ları göster
docker ps -a

# Disk kullanımını kontrol et
docker system df

# Kullanılmayan container/image'ları temizle
docker system prune -a

# Backend loglarını filtrele
docker-compose logs backend | grep ERROR

# Database'e hızlı bağlan
docker-compose exec postgres psql -U yasin yasin_trade_db
```

---

## 🆘 Destek

**Email:** support@yasin-trade.com
**Version:** 2026.1
**Last Updated:** 2026-02-06

---

**🎉 Başarılar! Projeniz hazır, şimdi geliştirmeye başlayabilirsiniz!**
