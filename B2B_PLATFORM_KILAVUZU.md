# 🏭 B2B Platform Kullanım Kılavuzu

## 📊 Platform Karşılaştırması

| Platform | Fiyat | MOQ | Dil | Ödeme | Kullanım | Öncelik |
|----------|-------|-----|-----|-------|----------|---------|
| **Alibaba** | Orta | Orta-Yüksek | İngilizce | Kredi Kartı | Kolay | ⭐⭐⭐⭐⭐ |
| **1688** | En Ucuz | Yüksek | Çince | Alipay | Zor | ⭐⭐⭐⭐ |
| **Made-in-China** | Orta | Orta | İngilizce | Kredi Kartı | Kolay | ⭐⭐⭐⭐ |
| **DHgate** | Orta-Yüksek | Düşük | İngilizce | Kredi Kartı | Kolay | ⭐⭐⭐ |
| **Global Sources** | Yüksek | Yüksek | İngilizce | Kredi Kartı | Orta | ⭐⭐⭐ |
| **Yiwugo** | Çok Ucuz | Düşük | Çince | Alipay | Zor | ⭐⭐⭐ |
| **Taobao** | Perakende | Yok | Çince | Alipay | Zor | ⭐⭐ |
| **AliExpress** | Pahalı | Yok | Türkçe | Kredi Kartı | Çok Kolay | ⭐ |

---

## 🎯 KULLANIM SENARYOLARI

### Senaryo 1: İlk Kez Toptan Alım (Yeni Başlayanlar)
```
Önerilen Sıra:
1. Alibaba.com → Ürün araştırması, fiyat karşılaştırma
2. DHgate → Küçük test siparişi (düşük MOQ)
3. Made-in-China → Alternatif tedarikçiler
```

### Senaryo 2: En Ucuz Fiyat (Deneyimli Alıcılar)
```
Önerilen Sıra:
1. 1688.com → En ucuz fabrika fiyatları (sourcing agent ile)
2. Yiwugo → Küçük ürünler için
3. Alibaba → Karşılaştırma için
```

### Senaryo 3: Dropshipping
```
Önerilen:
1. AliExpress → MOQ yok, hızlı başlangıç
2. DHgate → Alternatif
NOT: Toptan için uygun değil!
```

### Senaryo 4: Premium Kalite
```
Önerilen:
1. Global Sources → Doğrulanmış tedarikçiler
2. Made-in-China → Fabrika denetimleri
3. Alibaba Gold Suppliers
```

---

## 💰 FİYAT KARŞILAŞTIRMASI (Örnek: Smartphone Case)

```
1688.com:        $0.50 - $1.00  (En ucuz, Çince)
Yiwugo:          $0.60 - $1.20  (Çok ucuz, Çince)
Alibaba:         $1.00 - $2.00  (Orta, İngilizce) ⭐ ÖNERİLEN
Made-in-China:   $1.20 - $2.20  (Orta, İngilizce)
DHgate:          $1.50 - $2.50  (Düşük MOQ)
Global Sources:  $2.00 - $3.50  (Premium kalite)
AliExpress:      $3.00 - $5.00  (Perakende, MOQ yok)
```

**Sonuç:** 1688 en ucuz ama Çince ve sourcing agent gerekli. Alibaba en dengeli seçenek.

---

## 🔧 SOURCING AGENT KULLANIMI (1688 ve Taobao için)

### Popüler Sourcing Agent'lar:

1. **Superbuy** (En popüler)
   - Website: superbuy.com
   - Komisyon: %5-10
   - Avantaj: Türkçe destek, kolay kullanım

2. **Wegobuy**
   - Website: wegobuy.com
   - Komisyon: %5-8
   - Avantaj: Ucuz kargo

3. **CSSBuy**
   - Website: cssbuy.com
   - Komisyon: %3-5
   - Avantaj: En ucuz komisyon

4. **Yoybuy**
   - Website: yoybuy.com
   - Komisyon: %5-7
   - Avantaj: Hızlı teslimat

### Nasıl Kullanılır:

```bash
1. Agent sitesine kayıt ol
2. 1688 veya Taobao ürün linkini kopyala
3. Agent sitesine yapıştır
4. Agent senin için satın alır
5. Depoya gelince fotoğraf gönderir
6. Onaylarsan Türkiye'ye gönderir
```

**Toplam Maliyet:**
```
Ürün fiyatı (1688):     $100
Agent komisyon (%5):    $5
Kargo (deniz yolu):     $20
TOPLAM:                 $125

Alibaba ile karşılaştırma:
Ürün fiyatı (Alibaba):  $150
Kargo:                  $30
TOPLAM:                 $180

TASARRUF: $55 (30%)
```

---

## 📝 PLATFORM DETAYLARI

### 1. Alibaba.com ⭐ ÖNERİLEN
```python
# API Kullanımı
POST /api/v1/b2b/alibaba/search
{
  "query": "smartphone",
  "max_results": 20
}

# Avantajlar:
✅ İngilizce arayüz
✅ Trade Assurance (alıcı koruması)
✅ Kredi kartı ile ödeme
✅ Doğrulanmış tedarikçiler

# Dezavantajlar:
❌ 1688'den %30-50 daha pahalı
❌ MOQ genellikle yüksek (100-500 adet)
```

### 2. 1688.com (En Ucuz)
```python
# API Kullanımı
POST /api/v1/b2b/search
{
  "query": "smartphone",
  "platforms": ["1688"]
}

# UYARI: Sourcing agent gerekli!

# Avantajlar:
✅ En ucuz fiyatlar (fabrika direkt)
✅ 600,000+ fabrika
✅ Çin iç pazar fiyatları

# Dezavantajlar:
❌ Tamamen Çince
❌ Alipay zorunlu
❌ Sourcing agent komisyonu (%5-10)
❌ Satıcılar İngilizce bilmiyor

# Nasıl Kullanılır:
1. Superbuy, Wegobuy gibi agent kullan
2. Veya Çince bilen biri ile çalış
3. Alipay hesabı aç
```

### 3. Made-in-China
```python
# API Kullanımı
POST /api/v1/b2b/made-in-china/search
{
  "query": "industrial equipment",
  "max_results": 20
}

# Avantajlar:
✅ Endüstriyel ürünlerde güçlü
✅ Fabrika denetimleri
✅ İngilizce destek

# En İyi Kategoriler:
- Makine ve ekipman
- İnşaat malzemeleri
- Endüstriyel ürünler
```

### 4. DHgate (Düşük MOQ)
```python
# API Kullanımı
POST /api/v1/b2b/dhgate/search
{
  "query": "fashion accessories",
  "max_results": 20
}

# Avantajlar:
✅ Düşük MOQ (1-10 adet)
✅ Dropshipping için ideal
✅ Escrow ödeme

# Dezavantajlar:
❌ Fiyatlar Alibaba'dan biraz yüksek
❌ Kalite değişken
```

### 5. AliExpress (Perakende)
```python
# NOT: Toptan için UYGUN DEĞİL!

# Kullanım Alanları:
- Dropshipping
- Ürün testi (küçük miktarlar)
- Perakende satış

# Avantajlar:
✅ MOQ yok
✅ Türkçe arayüz
✅ Alıcı koruması

# Dezavantajlar:
❌ Alibaba'dan %50-100 daha pahalı
❌ Kargo yavaş (15-45 gün)
❌ Toptan fiyatı değil
```

---

## 🚀 HIZLI BAŞLANGIÇ REHBERİ

### Yeni Başlayanlar İçin:
```bash
1. Alibaba.com'da ürün araştır
2. 3-5 tedarikçi ile iletişime geç
3. Numune sipariş et (1-5 adet)
4. Kaliteyi test et
5. Toplu sipariş ver (100-500 adet)
```

### Deneyimli Alıcılar İçin:
```bash
1. 1688.com'da en ucuz fiyatı bul
2. Sourcing agent ile çalış (Superbuy)
3. Alibaba'da karşılaştır
4. En iyi fiyat/kalite dengesini seç
```

---

## 📞 SOURCING AGENT İLETİŞİM

### Superbuy
- Website: https://www.superbuy.com
- Email: service@superbuy.com
- WeChat: superbuy_service

### Wegobuy
- Website: https://www.wegobuy.com
- Email: service@wegobuy.com

### CSSBuy
- Website: https://www.cssbuy.com
- Email: service@cssbuy.com

---

**Son Güncelleme:** 2026-02-14  
**Durum:** Tüm platformlar eklendi, kullanıma hazır
