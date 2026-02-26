# 🔑 API Key Alma Kılavuzu

## Projeyi Çalıştırmak İçin Gerekli API Key'ler

### ✅ ZORUNLU: AI Provider (Birini Seç!)

Chatbot ve email kişiselleştirme için **mutlaka** bir AI provider seçmelisiniz:

---

#### ⭐ SEÇENEK 1: Groq (ÖNERİLEN - BEDAVA!)

**Neden Groq?**
- ✅ Tamamen ücretsiz
- ✅ Çok hızlı (Llama 3.1 modeli)
- ✅ Günlük 14,400 request limiti
- ✅ Kredi kartı gerektirmez

**Nasıl Alınır:**
1. https://console.groq.com/ adresine git
2. "Sign Up" ile hesap aç (Google ile giriş yapabilirsiniz)
3. Sol menüden "API Keys" seçeneğine tıkla
4. "Create API Key" butonuna tıkla
5. API key'i kopyala
6. `backend/.env` dosyasında `GROQ_API_KEY=` satırına yapıştır

**Örnek:**
```bash
GROQ_API_KEY=gsk_abc123xyz456...
```

---

#### SEÇENEK 2: OpenAI (Ücretli)

**Neden OpenAI?**
- En iyi AI kalitesi
- GPT-4 desteği
- Ancak ücretli (kullanım başına ödeme)

**Nasıl Alınır:**
1. https://platform.openai.com/ adresine git
2. Hesap aç (kredi kartı gerekli)
3. "API Keys" bölümüne git
4. "Create new secret key" tıkla
5. API key'i kopyala (bir daha gösterilmez!)
6. `backend/.env` dosyasında `OPENAI_API_KEY=` satırına yapıştır

**Maliyet:**
- GPT-3.5-turbo: ~$0.50 / 1M token
- GPT-4: ~$10 / 1M token

---

#### SEÇENEK 3: Hugging Face (Bedava)

**Neden Hugging Face?**
- Bedava
- Açık kaynak modeller
- Biraz yavaş olabilir

**Nasıl Alınır:**
1. https://huggingface.co/ adresine git
2. Hesap aç
3. Settings → Access Tokens
4. "New token" oluştur (Read yetkisi yeterli)
5. Token'ı kopyala
6. `backend/.env` dosyasında `HUGGINGFACE_API_KEY=` satırına yapıştır

---

### ⚠️ OPSİYONEL: Diğer API'ler

#### SendGrid (Email Gönderimi)

**Ne İçin:** Email kampanyaları göndermek için

**Nasıl Alınır:**
1. https://signup.sendgrid.com/ adresine git
2. Ücretsiz hesap aç (günlük 100 email bedava)
3. Settings → API Keys
4. "Create API Key" (Full Access)
5. API key'i kopyala
6. `backend/.env` dosyasında `SENDGRID_API_KEY=` satırına yapıştır

**Alternatif:** Resend API kullanabilirsiniz (daha modern)

---

#### Google Maps API (Scraping)

**Ne İçin:** Google Maps'ten firma bilgisi toplamak için

**Nasıl Alınır:**
1. https://console.cloud.google.com/ adresine git
2. Yeni proje oluştur
3. "APIs & Services" → "Credentials"
4. "Create Credentials" → "API Key"
5. Maps JavaScript API'yi aktif et
6. API key'i kopyala
7. `backend/.env` dosyasında `GOOGLE_MAPS_API_KEY=` satırına yapıştır

**Not:** Playwright ile scraping yapılıyor, API key opsiyonel

---

## 📝 .env Dosyası Örneği

```bash
# Database (Değiştirme!)
DATABASE_URL=postgresql+asyncpg://yasin:yasin123@postgres:5432/yasin_trade_db

# Security (Production'da değiştir!)
SECRET_KEY=yasin-secret-key-change-in-production-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ========================================
# AI PROVIDER - BİRİNİ SEÇ!
# ========================================

# GROQ (ÖNERİLEN - BEDAVA!)
GROQ_API_KEY=gsk_abc123xyz456...  # ← BURAYA YAPIŞT

IR

# Veya OpenAI (Ücretli)
# OPENAI_API_KEY=sk-proj-abc123...

# Veya Hugging Face (Bedava)
# HUGGINGFACE_API_KEY=hf_abc123...

# ========================================
# DİĞER API'LER (Opsiyonel)
# ========================================

# SendGrid (Email için - opsiyonel)
SENDGRID_API_KEY=SG.abc123...

# Google Maps (Scraping için - opsiyonel)
GOOGLE_MAPS_API_KEY=AIzaSy...

# Redis (Değiştirme!)
REDIS_URL=redis://redis:6379/0

# CORS
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

---

## 🚀 Hızlı Başlangıç

### Minimum Konfigürasyon (Sadece Chatbot)

```bash
# 1. Groq API key al (bedava!)
# https://console.groq.com/keys

# 2. backend/.env dosyasını düzenle
GROQ_API_KEY=gsk_your_key_here

# 3. Docker ile başlat
docker-compose up -d

# 4. Database migration
docker-compose exec backend alembic upgrade head

# 5. Test et
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

### Tam Konfigürasyon (Tüm Özellikler)

```bash
# 1. Tüm API key'leri al:
# - Groq (bedava) → Chatbot için
# - SendGrid (günlük 100 bedava) → Email için
# - Google Maps (opsiyonel) → Scraping için

# 2. backend/.env dosyasını düzenle
GROQ_API_KEY=gsk_...
SENDGRID_API_KEY=SG....
GOOGLE_MAPS_API_KEY=AIzaSy...

# 3. Projeyi başlat
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

---

## ❓ Sık Sorulan Sorular

### Hangi AI provider'ı seçmeliyim?

**Başlangıç için:** Groq (bedava, hızlı, yeterli)  
**En iyi kalite:** OpenAI GPT-4 (ücretli)  
**Açık kaynak:** Hugging Face (bedava, yavaş)

### Email göndermek zorunlu mu?

Hayır! Email kampanyaları opsiyonel. SendGrid API key olmadan da proje çalışır, sadece email gönderemezsiniz.

### Google Maps API olmadan çalışır mı?

Evet! Playwright ile scraping yapılıyor. Google Maps API sadece geocoding (adres → koordinat) için kullanılır.

### API key'leri nasıl test ederim?

```bash
# Backend'e gir
docker-compose exec backend bash

# Python REPL aç
python

# Test et
from app.core.config import settings
print(settings.GROQ_API_KEY)  # Key'i görmeli
```

---

## 🎯 Özet

**Minimum gereksinim:**
- ✅ Groq API key (BEDAVA!) → https://console.groq.com/keys

**Tam özellikler için:**
- ✅ Groq API key (chatbot)
- ⚠️ SendGrid API key (email - opsiyonel)
- ⚠️ Google Maps API key (scraping - opsiyonel)

**Toplam maliyet:** 0 TL (Groq bedava!)

---

**Son Güncelleme:** 2026-02-14  
**Destek:** ACIKLAMA.md dosyasına bakın
