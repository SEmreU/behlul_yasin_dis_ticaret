# 🚀 Projeyi Çalıştırma Kılavuzu

## Hızlı Başlangıç (5 Dakika)

### 1. API Key Al (BEDAVA!)

```bash
# Groq API key al (chatbot için - BEDAVA!)
# https://console.groq.com/keys adresine git
# Sign up yap → API Keys → Create API Key
# Key'i kopyala
```

### 2. .env Dosyasını Düzenle

```bash
cd backend
nano .env

# Bu satırı bul ve key'i yapıştır:
GROQ_API_KEY=gsk_your_key_here  # ← BURAYA YAPIŞT

IR
```

### 3. Docker ile Başlat

```bash
# Ana dizine dön
cd ..

# Servisleri başlat
docker-compose up -d

# Logları izle (opsiyonel)
docker-compose logs -f
```

### 4. Database Migration Çalıştır

```bash
# Backend container'ına gir
docker-compose exec backend bash

# Migration çalıştır
alembic upgrade head

# Çık
exit
```

### 5. Projeyi Aç

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🎯 Ne Yapıldı?

### ✅ Tamamlanan Özellikler

#### 1. Email Otomasyonu
- ✅ OpenAI ile email kişiselleştirme
- ✅ SendGrid entegrasyonu
- ✅ Email tracking (açılma, tıklama)
- ✅ Kampanya yönetimi

#### 2. AI Chatbot
- ✅ 3 AI provider desteği:
  - OpenAI GPT-3.5/4 (ücretli)
  - **Groq Llama 3** (BEDAVA!) ⭐
  - Hugging Face (bedava)
- ✅ Otomatik email/telefon toplama
- ✅ Çoklu dil desteği
- ✅ Lead yönetimi
- ✅ Conversation tracking

#### 3. Database
- ✅ Chatbot tabloları:
  - `chatbot_configs` - Bot ayarları
  - `chatbot_conversations` - Konuşmalar
  - `chatbot_leads` - Toplanan lead'ler
- ✅ User relationship'leri
- ✅ Migration hazır

#### 4. Backend
- ✅ 15 API endpoint grubu
- ✅ JWT authentication
- ✅ Multi-provider AI sistemi
- ✅ Automatic fallback

#### 5. Dokümantasyon
- ✅ ACIKLAMA.md - Kapsamlı geliştirici dokümantasyonu
- ✅ API_KEYS.md - API key alma kılavuzu
- ✅ QUICKSTART.md - Hızlı başlangıç
- ✅ DATABASE_SCHEMA.md - DB şeması

---

## 📋 Hangi API Key'ler Gerekli?

### Zorunlu (Chatbot için)

**Birini seç:**
- ⭐ **Groq** (ÖNERİLEN - BEDAVA!)
  - https://console.groq.com/keys
  - Günlük 14,400 request
  - Çok hızlı
  
- OpenAI (Ücretli)
  - https://platform.openai.com/api-keys
  - En iyi kalite
  - ~$0.50 / 1M token

- Hugging Face (Bedava)
  - https://huggingface.co/settings/tokens
  - Yavaş olabilir

### Opsiyonel

- **SendGrid** (Email gönderimi)
  - https://app.sendgrid.com/settings/api_keys
  - Günlük 100 email bedava
  
- **Google Maps** (Scraping)
  - https://console.cloud.google.com/apis/credentials
  - Playwright ile de çalışır

---

## 🔧 Kurulum Adımları (Detaylı)

### Adım 1: API Key'leri Al

Detaylı kılavuz: `API_KEYS.md`

**Minimum (Sadece chatbot):**
```bash
# Groq key al (bedava!)
# https://console.groq.com/keys
```

**Tam özellikler:**
```bash
# Groq → Chatbot
# SendGrid → Email
# Google Maps → Scraping (opsiyonel)
```

### Adım 2: .env Dosyasını Düzenle

```bash
cd backend
nano .env
```

**Minimum konfigürasyon:**
```bash
# AI Provider (Birini seç!)
GROQ_API_KEY=gsk_your_key_here  # ← BURAYA YAPIŞT

IR
```

**Tam konfigürasyon:**
```bash
# AI Provider
GROQ_API_KEY=gsk_...

# Email (opsiyonel)
SENDGRID_API_KEY=SG....

# Maps (opsiyonel)
GOOGLE_MAPS_API_KEY=AIzaSy...
```

### Adım 3: Dependencies Yükle

```bash
# Backend dependencies (Docker içinde otomatik)
cd backend
pip install -r requirements.txt

# Yeni eklenenler:
# - groq>=0.4.0 (Bedava AI)
```

### Adım 4: Docker ile Başlat

```bash
# Ana dizinde
docker-compose up -d

# Servisleri kontrol et
docker ps

# Şunları görmelisiniz:
# - yasin-trade-postgres
# - yasin-trade-redis
# - yasin-trade-backend
# - yasin-trade-frontend
```

### Adım 5: Database Migration

```bash
# Backend container'ına gir
docker-compose exec backend bash

# Migration çalıştır (chatbot tabloları oluşturulacak)
alembic upgrade head

# Çıktı:
# INFO  [alembic.runtime.migration] Running upgrade -> xxx, Add chatbot tables

# Çık
exit
```

### Adım 6: İlk Kullanıcı Oluştur

```bash
# API ile
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yasin.com",
    "password": "admin12345",
    "full_name": "Yasin Admin"
  }'

# Veya frontend'den
# http://localhost:3000/tr/register
```

---

## 🧪 Test Etme

### 1. Backend API Test

```bash
# Health check
curl http://localhost:8000/api/v1/health

# API docs aç
# http://localhost:8000/docs
```

### 2. Chatbot Test

```bash
# Chatbot config oluştur
curl -X POST http://localhost:8000/api/v1/chatbot/config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_name": "TradeBot",
    "welcome_message": "Merhaba! Size nasıl yardımcı olabilirim?",
    "supported_languages": ["tr", "en"],
    "goal": "both",
    "company_info": {"name": "Yasin Dış Ticaret"}
  }'

# Chatbot ile konuş (public endpoint)
curl -X POST http://localhost:8000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Merhaba, ürünleriniz hakkında bilgi almak istiyorum"
  }'

# AI yanıt alacaksınız!
```

### 3. Email Test

```bash
# Email kampanyası oluştur (SendGrid key gerekli)
curl -X POST http://localhost:8000/api/v1/campaigns/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "subject": "Merhaba {company_name}",
    "body": "Size özel teklifimiz var!",
    "company_ids": [1, 2, 3]
  }'
```

---

## 🐛 Sorun Giderme

### Problem: Docker servisleri başlamıyor

```bash
# Tüm container'ları durdur
docker-compose down

# Yeniden başlat
docker-compose up -d --build
```

### Problem: Database connection error

```bash
# PostgreSQL çalışıyor mu?
docker ps | grep postgres

# Logları kontrol et
docker-compose logs postgres
```

### Problem: Migration hatası

```bash
# Container'a gir
docker-compose exec backend bash

# Migration'ları sıfırla
alembic downgrade base

# Yeniden çalıştır
alembic upgrade head
```

### Problem: Chatbot yanıt vermiyor

```bash
# .env dosyasını kontrol et
cat backend/.env | grep GROQ_API_KEY

# Key doğru mu?
# Groq console'da kullanım limitini kontrol et
# https://console.groq.com/
```

### Problem: "Module not found" hatası

```bash
# Dependencies'i yeniden yükle
docker-compose exec backend pip install -r requirements.txt

# Container'ı yeniden başlat
docker-compose restart backend
```

---

## 📊 Proje Durumu

### ✅ Tamamlanan

- [x] Backend API (15 endpoint grubu)
- [x] Frontend (Next.js 15 + i18n)
- [x] Database şeması (8 tablo + 3 chatbot tablosu)
- [x] Authentication (JWT)
- [x] Email otomasyonu (OpenAI + SendGrid)
- [x] AI Chatbot (OpenAI + Groq + Hugging Face)
- [x] Chatbot database models
- [x] Lead management
- [x] Dokümantasyon

### ⚠️ Eksik (Opsiyonel)

- [ ] Frontend dashboard bileşenleri (gerçek veri entegrasyonu)
- [ ] Chatbot widget (embed edilebilir)
- [ ] Email template editor
- [ ] Harita görselleştirme
- [ ] B2B platform scraping
- [ ] Görsel arama

---

## 📚 Dokümantasyon

- **ACIKLAMA.md** - Kapsamlı geliştirici dokümantasyonu
- **API_KEYS.md** - API key alma kılavuzu
- **QUICKSTART.md** - Hızlı başlangıç
- **DATABASE_SCHEMA.md** - Veritabanı şeması
- **DEPLOYMENT.md** - Production deployment
- **API Docs** - http://localhost:8000/docs

---

## 🎉 Başarılar!

Projeniz hazır! Şimdi yapabilecekleriniz:

1. ✅ Chatbot ile konuşma
2. ✅ Email kampanyaları gönderme
3. ✅ Lead toplama
4. ✅ Kullanıcı kaydı
5. ✅ API kullanımı

**Minimum maliyet:** 0 TL (Groq bedava!)

---

**Son Güncelleme:** 2026-02-14  
**Versiyon:** 1.0.0  
**Destek:** ACIKLAMA.md
