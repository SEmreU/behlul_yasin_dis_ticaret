# 🔑 API Key Durumu ve Kullanım Kılavuzu

## ✅ ÇALIŞAN ÖZELLİKLER (API Key Olmadan)

### 1. AI Chatbot - Groq ✅
- **Durum:** TAM ÇALIŞIYOR
- **API Key:** Zaten ekli (`GROQ_API_KEY`)
- **Maliyet:** BEDAVA!
- **Test:** http://localhost:8000/docs → `/chatbot/chat`

### 2. Email Automation - SendGrid ⚠️
- **Durum:** Mock mode (email gönderilmiyor ama sistem çalışıyor)
- **API Key Gerekli:** SendGrid (opsiyonel)
- **Bedava Alternatif:** Günlük 100 email bedava
- **Test:** `/campaigns/create` endpoint'i çalışıyor

### 3. B2B Scraping - Alibaba ✅
- **Durum:** TAM ÇALIŞIYOR
- **API Key:** Gerektirmez (Playwright scraping)
- **Test:** `/b2b/alibaba/search`

---

## ⚠️ API KEY GEREKTİREN ÖZELLİKLER

### 1. Görsel Arama (Image Search)

**Gerekli:** OpenAI API Key (GPT-4 Vision)

**Maliyet:**
- Minimum $5 ödeme gerekli (2026'da)
- GPT-4 Vision: ~$10/1M token
- Yaklaşık 1000-2000 görsel analizi için yeterli

**Nasıl Alınır:**
1. https://platform.openai.com/ → Sign Up
2. Billing → Add payment method
3. Minimum $5 yükle
4. API Keys → Create new key
5. `.env` dosyasına ekle:
   ```bash
   OPENAI_API_KEY=sk-proj-abc123...
   ```

**Mock Mode:**
- API key yoksa sistem çalışır ama "API key gerekli" mesajı döner
- Test için yeterli

---

### 2. Google Maps Geocoding

**Gerekli:** Google Maps API Key

**Maliyet:**
- **BEDAVA:** Aylık $3,250 değerinde kullanım
- Geocoding: 10,000 request/ay bedava
- Yeni kullanıcılar: İlk 90 gün $300 kredi

**Nasıl Alınır:**
1. https://console.cloud.google.com/ → Proje oluştur
2. APIs & Services → Enable APIs:
   - Geocoding API
   - Maps JavaScript API
3. Credentials → Create API Key
4. API key'i kısıtla (güvenlik için)
5. `.env` dosyasına ekle:
   ```bash
   GOOGLE_MAPS_API_KEY=AIzaSy...
   ```

**Mock Mode:**
- API key yoksa mock koordinatlar döner
- Temel test için yeterli

---

### 3. TradeAtlas / ImportGenius

**Durum:** Ücretli subscription gerekli

**Maliyet:**
- TradeAtlas: ~$500-2000/ay
- ImportGenius: ~$1000+/ay

**Öneri:** Şimdilik atla, Alibaba scraping yeterli

---

## 🎯 ÖNERİLEN YAKLIŞIM

### Aşama 1: Şu Anda (BEDAVA) ✅
```bash
# Çalışan özellikler:
✅ AI Chatbot (Groq)
✅ Alibaba Scraping
✅ Email Automation (mock mode)
✅ Tüm diğer backend API'ler
```

### Aşama 2: İhtiyaç Halinde ($5-10)
```bash
# OpenAI API key ekle:
OPENAI_API_KEY=sk-proj-...

# Şunlar aktif olur:
✅ Görsel arama (GPT-4 Vision)
✅ Daha iyi email kişiselleştirme
✅ Gelişmiş chatbot (alternatif)
```

### Aşama 3: Production (BEDAVA)
```bash
# Google Maps API key ekle:
GOOGLE_MAPS_API_KEY=AIzaSy...

# Şunlar aktif olur:
✅ Geocoding (adres → koordinat)
✅ Harita görselleştirme (frontend)
✅ Yer detayları
```

---

## 🧪 TEST KOMUTLARI

### 1. Chatbot Test (Çalışıyor ✅)
```bash
curl -X POST http://localhost:8000/api/v1/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message": "Merhaba, ürünleriniz hakkında bilgi almak istiyorum"
  }'
```

### 2. Alibaba Scraping Test (Çalışıyor ✅)
```bash
# Önce login ol ve token al
TOKEN="your-jwt-token"

curl -X POST http://localhost:8000/api/v1/b2b/alibaba/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "smartphone", "max_results": 5}'
```

### 3. Görsel Arama Test (API key gerekli ⚠️)
```bash
# OpenAI API key ekledikten sonra:
curl -X POST http://localhost:8000/api/v1/search/image-search \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@product.jpg"
```

### 4. Email Campaign Test (Mock mode ✅)
```bash
curl -X POST http://localhost:8000/api/v1/campaigns/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "subject": "Hello {company_name}",
    "body_template": "We are interested in your products",
    "target_company_ids": [1, 2, 3]
  }'
```

---

## 💡 SONUÇ

**Şu Anda Kullanılabilir:**
- ✅ AI Chatbot (Groq - BEDAVA)
- ✅ B2B Scraping (Alibaba)
- ✅ Email Automation (mock mode)
- ✅ Tüm backend API'ler

**API Key Ekleyince Aktif Olur:**
- 🔑 Görsel arama (OpenAI - $5)
- 🔑 Geocoding (Google Maps - BEDAVA)
- 🔑 Email gönderimi (SendGrid - BEDAVA)

**Öneri:** Şimdilik mevcut özelliklerle test et. İhtiyaç olursa OpenAI ($5) ve Google Maps (bedava) ekle.

---

**Son Güncelleme:** 2026-02-14  
**Durum:** Backend %100 hazır, API keyler opsiyonel
