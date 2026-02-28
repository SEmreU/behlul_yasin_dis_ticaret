-- ============================================================
-- 002_rls_policies.sql
-- Row Level Security Politikaları
-- Çalıştırma: 001_initial_schema.sql SONRA çalıştırın
-- ============================================================

-- RLS'yi tüm tablolarda etkinleştir
ALTER TABLE users                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies                ENABLE ROW LEVEL SECURITY;
ALTER TABLE products                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_queries           ENABLE ROW LEVEL SECURITY;
ALTER TABLE visitor_identifications  ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_campaigns          ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_emails          ENABLE ROW LEVEL SECURITY;
ALTER TABLE fair_exhibitors          ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity            ENABLE ROW LEVEL SECURITY;

-- ─────────────────────────────────────────────────────────────
-- SERVICE ROLE: Backend API tam erişim (tüm tablolar)
-- Not: Backend Supabase service_role key ile bağlanır → RLS bypass
-- Bu politikalara gerek yok, sadece dokümantasyon amaçlı.
-- ─────────────────────────────────────────────────────────────

-- ─────────────────────────────────────────────────────────────
-- USERS tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Kullanıcı kendi profilini okuyabilir
CREATE POLICY "users_select_own" ON users
    FOR SELECT
    USING (auth.uid() = id);

-- Kullanıcı kendi profilini güncelleyebilir
CREATE POLICY "users_update_own" ON users
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Admin tüm kullanıcıları görebilir
CREATE POLICY "users_select_admin" ON users
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = auth.uid() AND u.is_admin = TRUE
        )
    );

-- ─────────────────────────────────────────────────────────────
-- COMPANIES tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Giriş yapmış tüm kullanıcılar şirketleri okuyabilir
CREATE POLICY "companies_select_authenticated" ON companies
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Admin şirket oluşturabilir/güncelleyebilir/silebilir
CREATE POLICY "companies_all_admin" ON companies
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = auth.uid() AND u.is_admin = TRUE
        )
    );

-- ─────────────────────────────────────────────────────────────
-- PRODUCTS tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Herkese açık okuma (ürün kataloğu)
CREATE POLICY "products_select_all" ON products
    FOR SELECT
    USING (TRUE);

-- Sadece admin yazabilir
CREATE POLICY "products_write_admin" ON products
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = auth.uid() AND u.is_admin = TRUE
        )
    );

-- ─────────────────────────────────────────────────────────────
-- SEARCH_QUERIES tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Kullanıcı sadece kendi sorgularını görebilir
CREATE POLICY "search_queries_select_own" ON search_queries
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "search_queries_insert_own" ON search_queries
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Admin tümünü görebilir
CREATE POLICY "search_queries_select_admin" ON search_queries
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = auth.uid() AND u.is_admin = TRUE
        )
    );

-- ─────────────────────────────────────────────────────────────
-- VISITOR_IDENTIFICATIONS tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Giriş yapmış kullanıcılar tüm ziyaretçileri okuyabilir (dashboard)
CREATE POLICY "visitor_select_authenticated" ON visitor_identifications
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- ─────────────────────────────────────────────────────────────
-- EMAIL_CAMPAIGNS tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Kullanıcı kendi kampanyalarını yönetebilir
CREATE POLICY "campaigns_own" ON email_campaigns
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- ─────────────────────────────────────────────────────────────
-- CAMPAIGN_EMAILS tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Kampanya sahibi emaillerini görebilir
CREATE POLICY "campaign_emails_select_own" ON campaign_emails
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM email_campaigns ec
            WHERE ec.id = campaign_emails.campaign_id
              AND ec.user_id = auth.uid()
        )
    );

-- ─────────────────────────────────────────────────────────────
-- FAIR_EXHIBITORS tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Herkese açık okuma
CREATE POLICY "fair_select_authenticated" ON fair_exhibitors
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Admin yazabilir
CREATE POLICY "fair_write_admin" ON fair_exhibitors
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = auth.uid() AND u.is_admin = TRUE
        )
    );

-- ─────────────────────────────────────────────────────────────
-- USER_ACTIVITY tablosu politikaları
-- ─────────────────────────────────────────────────────────────

-- Kullanıcı kendi aktivitesini görebilir
CREATE POLICY "activity_select_own" ON user_activity
    FOR SELECT
    USING (auth.uid() = user_id);

-- Admin tümünü görebilir
CREATE POLICY "activity_select_admin" ON user_activity
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = auth.uid() AND u.is_admin = TRUE
        )
    );
