# Yasin Dış Ticaret - Database Schema

## Entity Relationship Diagram

```
┌─────────────────────┐
│       users         │
├─────────────────────┤
│ id (PK)            │
│ email              │◄───────┐
│ hashed_password    │        │
│ full_name          │        │
│ subscription_tier  │        │  1:N
│ query_credits      │        │
│ is_active          │        │
│ created_at         │        │
└─────────────────────┘        │
                               │
                    ┌──────────┴──────────────┐
                    │                         │
        ┌───────────▼───────────┐   ┌────────▼────────────┐
        │   search_queries      │   │  email_campaigns    │
        ├───────────────────────┤   ├─────────────────────┤
        │ id (PK)              │   │ id (PK)             │
        │ user_id (FK)         │   │ user_id (FK)        │
        │ query_type           │   │ name                │
        │ query_parameters     │   │ subject             │
        │ results_count        │   │ body_template       │
        │ credits_used         │   │ total_recipients    │
        │ status               │   │ sent_count          │
        │ created_at           │   │ opened_count        │
        └──────────────────────┘   │ status              │
                                    │ scheduled_at        │
                                    └─────────┬───────────┘
                                              │ 1:N
                                    ┌─────────▼───────────┐
                                    │  campaign_emails    │
                                    ├─────────────────────┤
                                    │ id (PK)             │
                                    │ campaign_id (FK)    │
                                    │ company_id (FK)     │
                                    │ recipient_email     │
                                    │ is_sent             │
                                    │ is_opened           │
                                    │ tracking_id         │
                                    └─────────┬───────────┘
                                              │
                                    ┌─────────▼───────────┐
                                    │     companies       │
                                    ├─────────────────────┤
                                    │ id (PK)             │
                                    │ name                │◄────┐
                                    │ country             │     │
                                    │ website             │     │
                                    │ email               │     │ 1:N
                                    │ contact_emails      │     │
                                    │ latitude            │     │
                                    │ longitude           │     │
                                    │ source              │     │
                                    │ created_at          │     │
                                    └─────────────────────┘     │
                                                                │
                                    ┌───────────────────────────┘
                                    │
                        ┌───────────▼─────────────┐
                        │ visitor_identifications │
                        ├─────────────────────────┤
                        │ id (PK)                 │
                        │ session_id              │
                        │ ip_address              │
                        │ identified_company_id(FK)│
                        │ latitude                │
                        │ longitude               │
                        │ confidence_score        │
                        │ created_at              │
                        └─────────────────────────┘

┌─────────────────────┐        ┌─────────────────────┐
│      products       │        │   fair_exhibitors   │
├─────────────────────┤        ├─────────────────────┤
│ id (PK)            │        │ id (PK)             │
│ gtip_code          │        │ fair_name           │
│ oem_code           │        │ company_name        │
│ descriptions (JSON)│        │ booth_number        │
│ category           │        │ country             │
│ image_url          │        │ product_categories  │
│ created_at         │        │ match_score         │
└─────────────────────┘        │ fair_date           │
                               └─────────────────────┘
```

## Tablolar ve İlişkiler

### 1. `users` - Kullanıcı Yönetimi
**Amaç:** Platform kullanıcıları ve abonelik bilgileri

**Kolonlar:**
- `id`: Primary key
- `email`: Unique, kullanıcı email
- `hashed_password`: Bcrypt hash
- `subscription_tier`: Enum (FREE, PRO, ENTERPRISE)
- `query_credits`: Kalan sorgu kontörü
- `is_active`: Hesap aktif mi?
- `created_at`, `updated_at`: Timestamp'ler

**İlişkiler:**
- 1:N → search_queries
- 1:N → email_campaigns

---

### 2. `companies` - Firma Veritabanı
**Amaç:** Toplanan tüm firma bilgileri (scraping, manual entry)

**Kolonlar:**
- `id`: Primary key
- `name`: Firma adı (indexed)
- `country`, `city`, `address`: Lokasyon bilgileri
- `website`, `phone`, `email`: İletişim
- `contact_emails`: JSON array - [purchasing@, manager@, sales@]
- `latitude`, `longitude`: GPS koordinatları
- `source`: Veri kaynağı (google_maps, alibaba, fair, manual)
- `metadata`: JSON - Ek bilgiler

**İlişkiler:**
- 1:N → visitor_identifications
- N:M → campaign_emails (through campaign)

---

### 3. `products` - Ürün Kataloğu
**Amaç:** Ürün bilgileri, GTIP kodları, çoklu dil desteği

**Kolonlar:**
- `id`: Primary key
- `gtip_code`: GTIP/HS code (indexed)
- `oem_code`: OEM/Part number (indexed)
- `descriptions`: JSON - {"tr": "...", "en": "...", "de": "..."}
- `category`, `subcategory`: Kategoriler
- `image_url`: Ürün görseli
- `metadata`: JSON - Ek özellikler

**Kullanım:**
- Ürün arama modülü
- Fuar eşleştirme
- NLP/AI analizleri

---

### 4. `search_queries` - Arama Logları
**Amaç:** Kullanıcı aramalarını loglama, kontör takibi

**Kolonlar:**
- `id`: Primary key
- `user_id`: Foreign key → users
- `query_type`: Enum (product_search, map_scraping, fair_search, image_search)
- `query_parameters`: JSON - Arama parametreleri
- `results_count`: Bulunan sonuç sayısı
- `results_data`: JSON - Preview data
- `credits_used`: Harcanan kontör
- `status`: completed, failed, pending
- `error_message`: Hata durumunda mesaj

**İlişkiler:**
- N:1 → users

---

### 5. `visitor_identifications` - Ziyaretçi Tracking
**Amaç:** Web sitesi ziyaretçilerini kimliklendirme

**Kolonlar:**
- `id`: Primary key
- `session_id`: Unique session identifier
- `ip_address`: IP adresi (indexed)
- `user_agent`: Browser bilgisi
- `referer`: Nereden geldi
- `latitude`, `longitude`: GPS koordinatları
- `location_source`: gps | ip_geolocation
- `identified_company_id`: Foreign key → companies
- `confidence_score`: 0-1 arası eşleşme skoru
- `browser_fingerprint`: Canvas/WebGL fingerprint
- `location_permission_granted`: Boolean

**İlişkiler:**
- N:1 → companies

**Kullanım:**
- Modül 1: Ziyaretçi kimliklendirme
- Google Maps eşleştirme
- Real-time dashboard

---

### 6. `email_campaigns` - Email Kampanyaları
**Amaç:** Toplu mail gönderimi ve kampanya yönetimi

**Kolonlar:**
- `id`: Primary key
- `user_id`: Foreign key → users
- `name`: Kampanya adı
- `subject`, `body_template`: Email içeriği
- `target_company_ids`: JSON array - Hedef firma ID'leri
- `target_filters`: JSON - Filtre kriterleri
- `attachments`: JSON - [{"name": "catalog.pdf", "url": "..."}]
- `total_recipients`, `sent_count`, `opened_count`, `clicked_count`, `bounced_count`: İstatistikler
- `status`: Enum (draft, scheduled, sending, completed, paused)
- `scheduled_at`, `started_at`, `completed_at`: Zamanlama

**İlişkiler:**
- N:1 → users
- 1:N → campaign_emails

---

### 7. `campaign_emails` - Bireysel Email Tracking
**Amaç:** Her bir email'in tracking'i (açılma, tıklama)

**Kolonlar:**
- `id`: Primary key
- `campaign_id`: Foreign key → email_campaigns
- `company_id`: Foreign key → companies
- `recipient_email`, `recipient_name`: Alıcı bilgileri
- `personalized_subject`, `personalized_body`: AI ile kişiselleştirilmiş içerik
- `sent_at`, `opened_at`, `clicked_at`, `bounced_at`: Tracking timestamp'leri
- `is_sent`, `is_opened`, `is_clicked`, `is_bounced`: Boolean flags
- `tracking_id`: Unique tracking pixel/link ID

**İlişkiler:**
- N:1 → email_campaigns
- N:1 → companies

**Tracking Mekanizması:**
- Pixel tracking: `<img src="/track/pixel/{tracking_id}">`
- Link tracking: `/track/click/{tracking_id}`

---

### 8. `fair_exhibitors` - Fuar Katılımcıları
**Amaç:** Fuar verileri ve firma eşleştirme

**Kolonlar:**
- `id`: Primary key
- `fair_name`: Fuar adı (Hannover Messe, Canton Fair...)
- `fair_location`: Şehir, Ülke
- `fair_date`: Fuar tarihi (indexed)
- `company_name`: Katılımcı firma adı
- `booth_number`, `hall`: Stand bilgileri
- `country`, `city`, `website`, `email`, `phone`: İletişim
- `product_categories`: JSON array - Ürün kategorileri
- `product_description`: Text - Ürün açıklaması
- `match_score`: 0-100 - Kullanıcı ürünü ile eşleşme skoru
- `matched_keywords`: JSON - Eşleşen anahtar kelimeler

**Kullanım:**
- Modül 5: Fuar analizi
- NLP ile kullanıcı ürünü eşleştirme
- Competitor analysis

---

## İndeksler ve Performans

**Kritik İndeksler:**
```sql
-- users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);

-- companies
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_country ON companies(country);
CREATE INDEX idx_companies_source ON companies(source);

-- products
CREATE INDEX idx_products_gtip ON products(gtip_code);
CREATE INDEX idx_products_oem ON products(oem_code);

-- search_queries
CREATE INDEX idx_search_user ON search_queries(user_id);
CREATE INDEX idx_search_type ON search_queries(query_type);
CREATE INDEX idx_search_created ON search_queries(created_at);

-- visitor_identifications
CREATE INDEX idx_visitor_ip ON visitor_identifications(ip_address);
CREATE INDEX idx_visitor_session ON visitor_identifications(session_id);
CREATE INDEX idx_visitor_company ON visitor_identifications(identified_company_id);

-- email_campaigns
CREATE INDEX idx_campaign_user ON email_campaigns(user_id);
CREATE INDEX idx_campaign_status ON email_campaigns(status);

-- campaign_emails
CREATE INDEX idx_email_campaign ON campaign_emails(campaign_id);
CREATE INDEX idx_email_tracking ON campaign_emails(tracking_id);

-- fair_exhibitors
CREATE INDEX idx_fair_name ON fair_exhibitors(fair_name);
CREATE INDEX idx_fair_country ON fair_exhibitors(country);
CREATE INDEX idx_fair_date ON fair_exhibitors(fair_date);
```

## Migration Komutları

```bash
# Virtual environment aktif et
source venv/bin/activate

# İlk migration oluştur
alembic revision --autogenerate -m "Initial database schema"

# Migration'ı uygula
alembic upgrade head

# Son migration'ı geri al
alembic downgrade -1

# Tüm migration'ları geri al
alembic downgrade base
```

## Docker ile PostgreSQL Başlatma

```bash
# Docker Compose ile tüm servisleri başlat
docker-compose up -d

# Sadece PostgreSQL
docker-compose up -d postgres

# Database bağlantı testi
psql postgresql://yasin:yasin123@localhost:5432/yasin_trade_db
```

---

**Toplam Tablo Sayısı:** 8
**Toplam İlişki Sayısı:** 6 Foreign Key
**Estimated Storage (1M records):** ~5-10 GB

**GDPR/KVKK Uyumu:**
- created_at, updated_at tüm tablolarda
- Soft delete için is_deleted kolonları eklenebilir
- Kişisel veriler için encryption-at-rest (pgcrypto)
