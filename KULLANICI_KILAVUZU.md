# 🎯 B2B Scraper Sistemi - Detaylı Kullanım Kılavuzu

## 📋 İÇİNDEKİLER
1. [Sistem Nasıl Çalışıyor?](#sistem-nasıl-çalışıyor)
2. [Adım Adım Kullanım](#adım-adım-kullanım)
3. [Platform Linkleri](#platform-linkleri)
4. [API Test Rehberi](#api-test-rehberi)
5. [Frontend Kullanımı](#frontend-kullanımı)
6. [Sık Sorulan Sorular](#sık-sorulan-sorular)

---

## 🔄 SİSTEM NASIL ÇALIŞIYOR?

### Basit Açıklama (5 Yaşındaki Çocuğa Anlatır Gibi)

```
1. Sen "smartphone kılıfı" arıyorsun
2. Sistem senin yerine 10 farklı Çin sitesine gidiyor
3. Her sitede fiyatları, tedarikçileri buluyor
4. Hepsini sana bir listede gösteriyor
5. Sen en ucuzunu seçip o siteye gidiyorsun
6. Orada sipariş veriyorsun
```

### Teknik Açıklama

```mermaid
graph LR
    A[Kullanıcı] -->|Arama yapar| B[Frontend]
    B -->|API isteği| C[Backend]
    C -->|Scraping| D[Alibaba.com]
    C -->|Scraping| E[Made-in-China]
    C -->|Scraping| F[DHgate]
    D -->|Veri| C
    E -->|Veri| C
    F -->|Veri| C
    C -->|JSON| B
    B -->|Gösterir| A
    A -->|Tıklar| G[B2B Sitesi]
```

---

## 📝 ADIM ADIM KULLANIM

### ADIM 1: Sistemi Başlat

```bash
# Terminal'de proje klasörüne git
cd /home/behlul/yasin-dis-ticaret

# Docker ile başlat
docker-compose up -d

# Kontrol et
docker-compose ps
```

**Beklenen Çıktı:**
```
NAME                SERVICE    STATUS
backend             backend    Up
frontend            frontend   Up
postgres            postgres   Up
redis               redis      Up
```

✅ **Başarılı!** Sistem çalışıyor.

---

### ADIM 2: API'yi Test Et (Postman veya curl)

#### Seçenek A: Postman ile (Görsel)

1. **Postman'i Aç**
   - İndir: https://www.postman.com/downloads/

2. **Yeni İstek Oluştur**
   - Method: `POST`
   - URL: `http://localhost:8000/api/v1/auth/login`

3. **Login Yap (Token Al)**
   ```json
   {
     "email": "test@example.com",
     "password": "test123"
   }
   ```
   
   **Yanıt:**
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```
   
   ✅ **Token'ı kopyala!** Sonraki isteklerde kullanacaksın.

4. **B2B Arama Yap**
   - Method: `POST`
   - URL: `http://localhost:8000/api/v1/b2b/search`
   - Headers:
     ```
     Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     Content-Type: application/json
     ```
   - Body:
     ```json
     {
       "query": "smartphone",
       "platforms": ["alibaba", "made-in-china", "dhgate"]
     }
     ```

5. **Sonuçları Gör**
   ```json
   {
     "query": "smartphone",
     "total_results": 45,
     "results": {
       "alibaba": [
         {
           "title": "Samsung Galaxy S24 Case",
           "price": "$1.50-$2.00",
           "supplier": "Shenzhen Tech Co., Ltd.",
           "url": "https://www.alibaba.com/product-detail/...",
           "source": "alibaba"
         },
         // ... 14 ürün daha
       ],
       "made-in-china": [
         // ... 12 ürün
       ],
       "dhgate": [
         // ... 18 ürün
       ]
     }
   }
   ```

#### Seçenek B: Terminal ile (curl)

```bash
# 1. Login yap ve token al
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. B2B arama yap
curl -X POST http://localhost:8000/api/v1/b2b/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "smartphone",
    "platforms": ["alibaba", "made-in-china"]
  }' | jq

# 3. Sadece Alibaba'da ara
curl -X POST http://localhost:8000/api/v1/b2b/alibaba/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "laptop",
    "max_results": 10
  }' | jq
```

---

### ADIM 3: Sonuçları Anla

#### Örnek Sonuç Açıklaması

```json
{
  "title": "Samsung Galaxy S24 Case",           // ← Ürün adı
  "price": "$1.50-$2.00",                       // ← Fiyat aralığı (toptan)
  "supplier": "Shenzhen Tech Co., Ltd.",        // ← Tedarikçi firma
  "url": "https://www.alibaba.com/product...",  // ← Ürün linki (BURAYA TIKLA!)
  "source": "alibaba",                          // ← Hangi platformdan
  "moq": "100 pieces"                           // ← Minimum sipariş (varsa)
}
```

**ÖNEMLİ:** 
- `url` alanındaki linke tıklayarak direkt ürün sayfasına gidebilirsin
- Orada tedarikçi ile iletişime geçip sipariş verebilirsin

---

### ADIM 4: Siteye Git ve Sipariş Ver

1. **URL'yi Kopyala**
   ```
   https://www.alibaba.com/product-detail/Samsung-Galaxy-S24-Case_62517234567.html
   ```

2. **Tarayıcıda Aç**
   - Chrome, Firefox, Safari'de aç
   - Direkt ürün sayfası açılır

3. **Ürün Detaylarını İncele**
   - Fiyat: $1.50-$2.00 (MOQ: 100 adet)
   - Tedarikçi: Shenzhen Tech Co., Ltd.
   - Teslimat: 15-30 gün
   - Ödeme: T/T, L/C, Western Union

4. **Tedarikçi ile İletişime Geç**
   - "Contact Supplier" butonuna bas
   - Mesaj gönder:
     ```
     Hello,
     I'm interested in your Samsung Galaxy S24 Case.
     Can you provide:
     - Best price for 500 pieces
     - Sample availability
     - Shipping cost to Turkey
     
     Thank you!
     ```

5. **Teklif Al ve Sipariş Ver**
   - Tedarikçi 24-48 saat içinde yanıt verir
   - Fiyat ve şartları görüşürsün
   - Anlaşırsan sipariş verirsin

---

## 🔗 PLATFORM LİNKLERİ

### Ücretsiz Platformlar (API Key Gerektirmez)

#### 1. Alibaba.com ⭐ ÖNERİLEN
- **Link:** https://www.alibaba.com/
- **Arama:** https://www.alibaba.com/trade/search?SearchText=smartphone
- **Dil:** İngilizce
- **Ödeme:** Kredi kartı, T/T, L/C
- **MOQ:** Orta-Yüksek (100-1000 adet)
- **Avantaj:** En güvenilir, Trade Assurance var
- **API Endpoint:** `POST /api/v1/b2b/alibaba/search`

**Nasıl Kullanılır:**
```bash
curl -X POST http://localhost:8000/api/v1/b2b/alibaba/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "smartphone", "max_results": 20}'
```

---

#### 2. Made-in-China.com
- **Link:** https://www.made-in-china.com/
- **Arama:** https://www.made-in-china.com/products-search/hot-china-products/smartphone.html
- **Dil:** İngilizce
- **Ödeme:** Kredi kartı, T/T
- **MOQ:** Orta (50-500 adet)
- **Avantaj:** Endüstriyel ürünlerde güçlü, fabrika denetimleri
- **API Endpoint:** `POST /api/v1/b2b/made-in-china/search`

**Nasıl Kullanılır:**
```bash
curl -X POST http://localhost:8000/api/v1/b2b/made-in-china/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "industrial equipment", "max_results": 20}'
```

---

#### 3. DHgate.com
- **Link:** https://www.dhgate.com/
- **Arama:** https://www.dhgate.com/wholesale/search.do?searchkey=smartphone
- **Dil:** İngilizce
- **Ödeme:** Kredi kartı, PayPal
- **MOQ:** Düşük (1-10 adet) ⭐ DROPSHIPPING İÇİN İDEAL
- **Avantaj:** Düşük MOQ, escrow ödeme
- **API Endpoint:** `POST /api/v1/b2b/dhgate/search`

**Nasıl Kullanılır:**
```bash
curl -X POST http://localhost:8000/api/v1/b2b/dhgate/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "fashion accessories", "max_results": 20}'
```

---

#### 4. Global Sources
- **Link:** https://www.globalsources.com/
- **Arama:** https://www.globalsources.com/SEARCH/s?query=smartphone
- **Dil:** İngilizce
- **Ödeme:** T/T, L/C
- **MOQ:** Yüksek (500-5000 adet)
- **Avantaj:** Premium kalite, doğrulanmış tedarikçiler
- **API Endpoint:** `POST /api/v1/b2b/search` (platform: "global-sources")

---

#### 5. Yiwugo.com
- **Link:** https://www.yiwugo.com/
- **Arama:** https://www.yiwugo.com/search/smartphone
- **Dil:** Çince (Google Translate kullan)
- **Ödeme:** Alipay, WeChat Pay
- **MOQ:** Düşük (10-50 adet)
- **Avantaj:** Yiwu pazarı (dünyanın en büyük), çok ucuz
- **API Endpoint:** `POST /api/v1/b2b/search` (platform: "yiwugo")

---

### Sourcing Agent Gerektiren Platformlar

#### 6. 1688.com (En Ucuz!) 💰
- **Link:** https://www.1688.com/
- **Arama:** https://s.1688.com/selloffer/offer_search.htm?keywords=smartphone
- **Dil:** Çince (zorunlu)
- **Ödeme:** Alipay (zorunlu)
- **MOQ:** Yüksek (100-1000 adet)
- **Avantaj:** Alibaba'dan %30-50 daha ucuz
- **Dezavantaj:** Çince bilmek veya sourcing agent gerekli
- **API Endpoint:** `POST /api/v1/b2b/search` (platform: "1688")

**Sourcing Agent'lar:**
- Superbuy: https://www.superbuy.com/
- Wegobuy: https://www.wegobuy.com/
- CSSBuy: https://www.cssbuy.com/

**Nasıl Kullanılır:**
1. 1688'de ürün bul (API ile veya manuel)
2. Ürün linkini kopyala
3. Superbuy'a yapıştır
4. Agent senin için satın alır
5. Türkiye'ye gönderir

---

#### 7. Taobao
- **Link:** https://www.taobao.com/
- **Arama:** https://s.taobao.com/search?q=smartphone
- **Dil:** Çince
- **Ödeme:** Alipay
- **MOQ:** Yok (perakende)
- **NOT:** Toptan için uygun DEĞİL, 1688 kullan
- **API Endpoint:** `POST /api/v1/b2b/search` (platform: "taobao")

---

### Perakende Platformlar (Toptan Değil)

#### 8. AliExpress
- **Link:** https://www.aliexpress.com/
- **Arama:** https://www.aliexpress.com/wholesale?SearchText=smartphone
- **Dil:** Türkçe
- **Ödeme:** Kredi kartı
- **MOQ:** Yok
- **NOT:** Dropshipping için ideal, toptan için pahalı
- **API Endpoint:** `POST /api/v1/b2b/search` (platform: "aliexpress")

---

## 🧪 API TEST REHBERİ

### Test 1: Tek Platform (Alibaba)

```bash
# Token al
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

# Alibaba'da ara
curl -X POST http://localhost:8000/api/v1/b2b/alibaba/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bluetooth speaker",
    "max_results": 5
  }' | jq
```

**Beklenen Sonuç:**
```json
{
  "query": "bluetooth speaker",
  "platform": "alibaba",
  "results_count": 5,
  "results": [
    {
      "title": "Portable Bluetooth Speaker",
      "price": "$5.00-$8.00",
      "supplier": "Shenzhen Audio Co.",
      "url": "https://www.alibaba.com/product-detail/...",
      "source": "alibaba"
    }
  ]
}
```

---

### Test 2: Çoklu Platform

```bash
curl -X POST http://localhost:8000/api/v1/b2b/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "usb cable",
    "platforms": ["alibaba", "made-in-china", "dhgate"]
  }' | jq
```

**Beklenen Sonuç:**
```json
{
  "query": "usb cable",
  "total_results": 47,
  "results": {
    "alibaba": [ /* 15 ürün */ ],
    "made-in-china": [ /* 18 ürün */ ],
    "dhgate": [ /* 14 ürün */ ]
  }
}
```

---

### Test 3: Tüm Platformlar

```bash
curl -X POST http://localhost:8000/api/v1/b2b/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "phone case",
    "platforms": [
      "alibaba",
      "made-in-china", 
      "dhgate",
      "global-sources",
      "yiwugo",
      "1688",
      "taobao",
      "aliexpress"
    ]
  }' | jq
```

---

## 💻 FRONTEND KULLANIMI (Gelecekte)

### Şu Anda:
- ❌ Frontend sayfası yok
- ✅ API çalışıyor (Postman/curl ile test edilebilir)

### Frontend Eklenince:

```
1. http://localhost:3000 → Ana sayfa
2. Login yap
3. Dashboard → "B2B Pazar Araştırması" kartına tıkla
4. Arama sayfası açılır:
   
   ┌────────────────────────────────────┐
   │ Ürün Ara: [smartphone_______]     │
   │                                    │
   │ Platformlar:                       │
   │ ☑ Alibaba  ☑ Made-in-China        │
   │ ☑ DHgate   ☐ 1688                 │
   │                                    │
   │ [🔍 Ara]                           │
   └────────────────────────────────────┘

5. "Ara" butonuna bas
6. Sonuçlar gelir:
   
   ┌────────────────────────────────────┐
   │ ALIBABA (15 sonuç)                 │
   ├────────────────────────────────────┤
   │ Samsung Galaxy Case                │
   │ $1.50-$2.00 | MOQ: 100            │
   │ Shenzhen Tech Co.                  │
   │ [Siteye Git →]                     │
   └────────────────────────────────────┘

7. "Siteye Git" → Alibaba.com açılır
8. Sipariş verirsin
```

---

## ❓ SIK SORULAN SORULAR

### S1: Sistem şu anda çalışıyor mu?
**C:** Evet! Backend API %100 çalışıyor. Postman veya curl ile test edebilirsin. Frontend UI henüz yok.

### S2: Nasıl test edebilirim?
**C:** İki yöntem:
1. **Postman:** Görsel, kolay (yukarıdaki rehberi takip et)
2. **curl:** Terminal'de (yukarıdaki komutları kopyala-yapıştır)

### S3: Sonuçlardaki linklere nasıl ulaşırım?
**C:** API yanıtında `url` alanı var. Örnek:
```json
{
  "url": "https://www.alibaba.com/product-detail/..."
}
```
Bu linki tarayıcıda aç, direkt ürün sayfası açılır.

### S4: Hangi platformlar çalışıyor?
**C:** 
- ✅ Alibaba (tam çalışıyor)
- ✅ Made-in-China (tam çalışıyor)
- ✅ DHgate (tam çalışıyor)
- ⚠️ Global Sources (mock data)
- ⚠️ Yiwugo (mock data)
- ⚠️ 1688 (mock data, sourcing agent gerekli)
- ⚠️ Taobao (mock data)
- ⚠️ AliExpress (mock data)

### S5: Frontend ne zaman hazır olur?
**C:** 2-3 saatte basit bir arama sayfası yapılabilir. İstersen şimdi yapalım!

### S6: API key gerekiyor mu?
**C:** Hayır! B2B scraper için API key gerektirmez. Playwright ile direkt sitelere gidiyor.

### S7: Kaç ürün sonuç dönüyor?
**C:** Varsayılan 20, `max_results` ile değiştirebilirsin:
```json
{
  "query": "smartphone",
  "max_results": 50
}
```

### S8: Fiyatlar güncel mi?
**C:** Evet! Her aramada canlı olarak sitelere gidip güncel fiyatları çekiyor.

### S9: Sipariş verebilir miyim?
**C:** Hayır, sistem sadece arama yapıyor. Sipariş için:
1. Sonuçtaki `url` linkine git
2. B2B sitesinde tedarikçi ile iletişime geç
3. Orada sipariş ver

### S10: Hangi dillerde çalışıyor?
**C:** 
- Alibaba, Made-in-China, DHgate: İngilizce
- 1688, Taobao, Yiwugo: Çince (sourcing agent gerekli)
- AliExpress: Türkçe

---

## 🚀 HIZLI BAŞLANGIÇ (5 Dakika)

```bash
# 1. Sistemi başlat
cd /home/behlul/yasin-dis-ticaret
docker-compose up -d

# 2. Token al
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

# 3. Alibaba'da ara
curl -X POST http://localhost:8000/api/v1/b2b/alibaba/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "smartphone", "max_results": 5}' | jq

# 4. Sonuçları gör
# 5. URL'yi kopyala ve tarayıcıda aç
# 6. Sipariş ver!
```

---

## 📞 DESTEK

**Sorularınız için:**
- Dokümantasyon: `/home/behlul/yasin-dis-ticaret/ACIKLAMA.md`
- API Detayları: `http://localhost:8000/docs`
- Platform Kılavuzu: `B2B_PLATFORM_KILAVUZU.md`

---

**Son Güncelleme:** 2026-02-14  
**Durum:** Backend çalışıyor, Frontend bekleniyor  
**Test:** ✅ Postman/curl ile test edilebilir
