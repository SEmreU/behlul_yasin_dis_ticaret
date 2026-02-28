-- ============================================================
-- seed.sql — Başlangıç Verisi
-- Çalıştırma: Tüm migration'lardan SONRA çalıştırın
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- Admin kullanıcı oluştur
-- ⚠ ŞİFREYİ DEĞİŞTİRİN: bcrypt hash'i aşağıdaki gibi üretin:
--   python3 -c "from passlib.hash import bcrypt; print(bcrypt.hash('YeniSifre123!'))"
-- ─────────────────────────────────────────────────────────────
INSERT INTO users (
    id,
    email,
    hashed_password,
    full_name,
    subscription_tier,
    query_credits,
    is_active,
    is_admin
) VALUES (
    uuid_generate_v4(),
    'admin@yasin-trade.com',
    -- Bu geçici hash: şifre = 'Admin123!' → Lütfen değiştirin!
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMeJf85zm8vG.9zJ.Zcb7BvJ2',
    'Admin Kullanıcı',
    'ENTERPRISE',
    99999,
    TRUE,
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- ─────────────────────────────────────────────────────────────
-- Örnek ülke listesi (companies için lookup)
-- ─────────────────────────────────────────────────────────────
INSERT INTO companies (name, country, city, source) VALUES
    ('Örnek Çin Firması A', 'China', 'Guangzhou', 'seed'),
    ('Örnek Almanya Firması B', 'Germany', 'Frankfurt', 'seed'),
    ('Örnek Hindistan Firması C', 'India', 'Mumbai', 'seed')
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────────────────────────
-- Örnek ürünler (GTIP ve OEM örnekleri)
-- ─────────────────────────────────────────────────────────────
INSERT INTO products (gtip_code, oem_code, descriptions, category) VALUES
    ('8708.29.10.00', 'ABC-12345', '{"tr": "Araç tampon parçası", "en": "Vehicle bumper part"}', 'Automotive'),
    ('8544.42.90.00', 'XYZ-67890', '{"tr": "Elektrik kablosu demeti", "en": "Wiring harness"}', 'Electronics')
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────────────────────────
-- Örnek fuar verisi
-- ─────────────────────────────────────────────────────────────
INSERT INTO fair_exhibitors (fair_name, fair_location, fair_date, company_name, country) VALUES
    ('Hannover Messe 2025', 'Hannover, Germany', '2025-04-07', 'SampleCo GmbH', 'Germany'),
    ('Canton Fair 2025', 'Guangzhou, China', '2025-04-15', 'Guangzhou Sample Ltd', 'China')
ON CONFLICT DO NOTHING;

-- ─────────────────────────────────────────────────────────────
-- PRODUCTION NOT:
-- Yukarıdaki örnek veriler (companies, products, fair_exhibitors)
-- production'da temizlenebilir. Admin kullanıcıyı kesinlikle güncelleyin.
-- ─────────────────────────────────────────────────────────────
