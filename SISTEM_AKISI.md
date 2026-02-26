# 🔄 B2B Platform Scraper - Sistem Akışı

## 📊 SİSTEM NASIL ÇALIŞIYOR?

### Mevcut Durum (Backend Hazır ✅)

```
Kullanıcı → Frontend → Backend API → Scraper → B2B Siteleri
                                         ↓
                                    Veri Döner
                                         ↓
                            Frontend'de Gösterilir
```

### Detaylı Akış:

1. **Kullanıcı Arama Yapar**
   - Frontend'de "Alibaba'da smartphone ara" der
   - Arama isteği backend'e gider

2. **Backend Scraper Çalışır**
   - Playwright ile Alibaba.com'a gider
   - Ürün listesini çeker (başlık, fiyat, tedarikçi)
   - JSON formatında döndürür

3. **Frontend Sonuçları Gösterir**
   - Tablo veya kart görünümünde
   - Fiyat, tedarikçi, link bilgileri
   - "Siteye Git" butonu ile direkt Alibaba'ya yönlendirir

---

## 🎯 KULLANICI DENEYİMİ

### Senaryo: Kullanıcı Ürün Arıyor

```
1. Kullanıcı dashboard'a giriş yapar
2. "B2B Pazar Araştırması" sayfasına gider
3. Arama kutusu:
   - Ürün adı: "smartphone"
   - Platformlar: [✓] Alibaba [✓] Made-in-China [✓] DHgate
   - "Ara" butonuna basar

4. Sistem 3 platformda arama yapar (paralel)
5. Sonuçlar gelir:

   ┌─────────────────────────────────────────┐
   │ ALIBABA (15 sonuç)                      │
   ├─────────────────────────────────────────┤
   │ Samsung Galaxy Case                     │
   │ Fiyat: $1.50-$2.00                     │
   │ Tedarikçi: Shenzhen Tech Co.           │
   │ MOQ: 100 pieces                        │
   │ [Siteye Git →]                         │
   ├─────────────────────────────────────────┤
   │ iPhone 15 Case                         │
   │ Fiyat: $2.00-$3.00                     │
   │ ...                                    │
   └─────────────────────────────────────────┘

   ┌─────────────────────────────────────────┐
   │ MADE-IN-CHINA (12 sonuç)               │
   ├─────────────────────────────────────────┤
   │ ...                                    │
   └─────────────────────────────────────────┘

6. Kullanıcı ilgisini çeken ürüne tıklar
7. "Siteye Git" butonu ile Alibaba'ya yönlendirilir
8. Alibaba'da sipariş verir
```

---

## 💻 FRONTEND ENTEGRASYONU (Eksik Kısım)

### Şu Anda:
- ❌ Frontend sayfası YOK
- ✅ Backend API hazır
- ✅ Scraper çalışıyor

### Yapılması Gerekenler:

#### 1. B2B Arama Sayfası Oluştur
```typescript
// frontend/app/[locale]/b2b-search/page.tsx

"use client"
import { useState } from 'react'

export default function B2BSearchPage() {
  const [query, setQuery] = useState('')
  const [platforms, setPlatforms] = useState(['alibaba'])
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    setLoading(true)
    
    const response = await fetch('http://localhost:8000/api/v1/b2b/search', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query, platforms })
    })
    
    const data = await response.json()
    setResults(data.results)
    setLoading(false)
  }

  return (
    <div>
      <h1>B2B Pazar Araştırması</h1>
      
      {/* Arama Formu */}
      <input 
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ürün ara..."
      />
      
      {/* Platform Seçimi */}
      <div>
        <label>
          <input type="checkbox" value="alibaba" />
          Alibaba
        </label>
        <label>
          <input type="checkbox" value="made-in-china" />
          Made-in-China
        </label>
        {/* ... diğer platformlar */}
      </div>
      
      <button onClick={handleSearch}>Ara</button>
      
      {/* Sonuçlar */}
      {Object.entries(results).map(([platform, items]) => (
        <div key={platform}>
          <h2>{platform.toUpperCase()} ({items.length} sonuç)</h2>
          {items.map((item, i) => (
            <div key={i} className="product-card">
              <h3>{item.title}</h3>
              <p>Fiyat: {item.price}</p>
              <p>Tedarikçi: {item.supplier}</p>
              <a href={item.url} target="_blank">
                Siteye Git →
              </a>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
```

#### 2. Dashboard'a Ekle
```typescript
// frontend/app/[locale]/dashboard/page.tsx

<Link href="/b2b-search">
  <Card>
    <CardTitle>B2B Pazar Araştırması</CardTitle>
    <CardDescription>
      10 farklı platformda ürün ara
    </CardDescription>
  </Card>
</Link>
```

---

## 🔄 VERİ AKIŞI DETAYLI

### 1. Kullanıcı Arama Yapar
```javascript
// Frontend
POST /api/v1/b2b/search
{
  "query": "smartphone case",
  "platforms": ["alibaba", "made-in-china", "dhgate"]
}
```

### 2. Backend Scraper Çalışır
```python
# Backend (app/services/b2b_scraper.py)
async def search_all_platforms(query, platforms):
    results = {}
    
    # Alibaba'da ara
    alibaba_results = await AlibabaScraper.search_products(query)
    # → Playwright ile Alibaba.com'a gider
    # → Ürün listesini çeker
    # → JSON döndürür
    
    results['alibaba'] = alibaba_results
    # ... diğer platformlar
    
    return results
```

### 3. Scraper Alibaba'ya Gider
```python
# Playwright ile
browser = await p.chromium.launch()
page = await browser.new_page()

# Alibaba arama sayfası
await page.goto(f"https://www.alibaba.com/trade/search?SearchText={query}")

# Ürünleri çek
products = await page.query_selector_all('.organic-list-offer')

for product in products:
    title = await product.query_selector('.title')
    price = await product.query_selector('.price')
    # ...
```

### 4. Veri Döner
```json
{
  "alibaba": [
    {
      "title": "Samsung Galaxy S24 Case",
      "price": "$1.50-$2.00",
      "supplier": "Shenzhen Tech Co., Ltd.",
      "url": "https://alibaba.com/product/...",
      "source": "alibaba"
    },
    // ... 19 ürün daha
  ],
  "made-in-china": [
    // ...
  ],
  "dhgate": [
    // ...
  ]
}
```

### 5. Frontend Gösterir
```jsx
{results.alibaba.map(product => (
  <ProductCard>
    <h3>{product.title}</h3>
    <p>{product.price}</p>
    <a href={product.url}>Siteye Git →</a>
  </ProductCard>
))}
```

---

## 📱 KULLANICI ARAYÜZÜ TASARIMI

### Ana Sayfa (Dashboard)
```
┌────────────────────────────────────────┐
│  Yasin Dış Ticaret                     │
├────────────────────────────────────────┤
│                                        │
│  [📊 Dashboard]  [🔍 B2B Arama]       │
│  [📧 Email]      [🤖 Chatbot]         │
│                                        │
└────────────────────────────────────────┘
```

### B2B Arama Sayfası
```
┌────────────────────────────────────────┐
│  🔍 B2B Pazar Araştırması              │
├────────────────────────────────────────┤
│                                        │
│  Ürün Ara: [smartphone case_______]   │
│                                        │
│  Platformlar:                          │
│  ☑ Alibaba      ☑ Made-in-China       │
│  ☑ DHgate       ☐ 1688 (Çince)        │
│  ☐ Global Sources                      │
│                                        │
│  [🔍 Ara]                              │
│                                        │
├────────────────────────────────────────┤
│  SONUÇLAR (45 ürün bulundu)           │
├────────────────────────────────────────┤
│                                        │
│  📦 ALIBABA (15 sonuç)                │
│  ┌──────────────────────────────────┐ │
│  │ Samsung Galaxy S24 Case          │ │
│  │ 💰 $1.50-$2.00 | MOQ: 100       │ │
│  │ 🏭 Shenzhen Tech Co.            │ │
│  │ [Siteye Git →]                  │ │
│  └──────────────────────────────────┘ │
│  ┌──────────────────────────────────┐ │
│  │ iPhone 15 Pro Case               │ │
│  │ ...                              │ │
│  └──────────────────────────────────┘ │
│                                        │
│  📦 MADE-IN-CHINA (12 sonuç)          │
│  ...                                   │
│                                        │
└────────────────────────────────────────┘
```

---

## 🎯 ÖZELLİKLER

### Temel Özellikler (Şu An Çalışır)
- ✅ 10 platformda arama
- ✅ Paralel scraping (hızlı)
- ✅ Fiyat, tedarikçi, link bilgisi
- ✅ API hazır

### Eklenecek Özellikler (Frontend)
- ❌ Arama sayfası UI
- ❌ Sonuç gösterimi
- ❌ Filtreleme (fiyat, MOQ)
- ❌ Karşılaştırma tablosu
- ❌ Favorilere ekleme
- ❌ Excel export

---

## 💡 KULLANIM ÖRNEĞİ

### API Test (Şu An Çalışır)
```bash
# Terminal'de test et
curl -X POST http://localhost:8000/api/v1/b2b/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "smartphone",
    "platforms": ["alibaba", "made-in-china"]
  }'

# Sonuç:
{
  "alibaba": [
    {
      "title": "Samsung Case",
      "price": "$1.50",
      "url": "https://alibaba.com/..."
    }
  ],
  "made-in-china": [...]
}
```

### Frontend'de Kullanım (Yapılacak)
```typescript
// Kullanıcı arama yapar
const searchB2B = async () => {
  const response = await fetch('/api/v1/b2b/search', {
    method: 'POST',
    body: JSON.stringify({
      query: 'smartphone',
      platforms: ['alibaba', 'made-in-china']
    })
  })
  
  const data = await response.json()
  // data.alibaba → Alibaba sonuçları
  // data['made-in-china'] → Made-in-China sonuçları
  
  setResults(data)
}
```

---

## 📊 SONUÇ

### Mevcut Durum:
- ✅ Backend API %100 hazır
- ✅ 10 platform scraper çalışıyor
- ❌ Frontend UI eksik

### Kullanıcı Ne Yapabilir:
1. **Şimdi:** API'yi Postman ile test edebilir
2. **Frontend Eklenince:** Web sitesinde arama yapıp sonuçları görebilir
3. **Akış:** Ara → Sonuçları gör → İlgili siteye git → Sipariş ver

### Sonraki Adım:
Frontend sayfası oluşturmak gerekiyor. Yapalım mı?

---

**Durum:** Backend hazır, frontend UI bekleniyor  
**Tahmini Süre:** 2-3 saat (frontend sayfası)
