-- ============================================================
-- 003_functions.sql
-- Trigger Fonksiyonları ve RPC'ler
-- Çalıştırma: 002_rls_policies.sql SONRA çalıştırın
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- updated_at otomatik güncelleme trigger'ı
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger'ları ilgili tablolara bağla
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_campaigns_updated_at
    BEFORE UPDATE ON email_campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ─────────────────────────────────────────────────────────────
-- Şirket arama fonksiyonu (full-text + trigram)
-- Kullanım: SELECT * FROM search_companies('plastik makine', 'Germany', 20);
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION search_companies(
    search_term  TEXT,
    country_filter TEXT DEFAULT NULL,
    limit_count  INTEGER DEFAULT 20
)
RETURNS TABLE (
    id          UUID,
    name        TEXT,
    country     TEXT,
    city        TEXT,
    website     TEXT,
    email       TEXT,
    source      TEXT,
    similarity  REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.country,
        c.city,
        c.website,
        c.email,
        c.source,
        similarity(c.name, search_term) AS similarity
    FROM companies c
    WHERE
        (country_filter IS NULL OR c.country ILIKE '%' || country_filter || '%')
        AND (
            c.name ILIKE '%' || search_term || '%'
            OR similarity(c.name, search_term) > 0.2
        )
    ORDER BY similarity(c.name, search_term) DESC, c.name
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ─────────────────────────────────────────────────────────────
-- Kullanıcı istatistikleri RPC'si
-- Kullanım: SELECT * FROM get_user_stats('user-uuid');
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION get_user_stats(target_user_id UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_searches',     (SELECT COUNT(*) FROM search_queries WHERE user_id = target_user_id),
        'total_campaigns',    (SELECT COUNT(*) FROM email_campaigns WHERE user_id = target_user_id),
        'emails_sent',        (SELECT COALESCE(SUM(sent_count), 0) FROM email_campaigns WHERE user_id = target_user_id),
        'credits_remaining',  (SELECT query_credits FROM users WHERE id = target_user_id),
        'subscription',       (SELECT subscription_tier FROM users WHERE id = target_user_id),
        'last_activity',      (SELECT MAX(created_at) FROM search_queries WHERE user_id = target_user_id)
    ) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ─────────────────────────────────────────────────────────────
-- Admin dashboard istatistikleri
-- Kullanım: SELECT * FROM get_admin_stats();
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION get_admin_stats()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_users',         (SELECT COUNT(*) FROM users WHERE is_active = TRUE),
        'pro_users',           (SELECT COUNT(*) FROM users WHERE subscription_tier = 'PRO'),
        'enterprise_users',    (SELECT COUNT(*) FROM users WHERE subscription_tier = 'ENTERPRISE'),
        'total_companies',     (SELECT COUNT(*) FROM companies),
        'total_searches_today',(SELECT COUNT(*) FROM search_queries WHERE created_at >= CURRENT_DATE),
        'total_campaigns',     (SELECT COUNT(*) FROM email_campaigns),
        'total_emails_sent',   (SELECT COALESCE(SUM(sent_count), 0) FROM email_campaigns),
        'visitors_today',      (SELECT COUNT(*) FROM visitor_identifications WHERE created_at >= CURRENT_DATE)
    ) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ─────────────────────────────────────────────────────────────
-- Kredi azaltma fonksiyonu
-- Kullanım: SELECT deduct_credits('user-uuid', 2);
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION deduct_credits(
    target_user_id UUID,
    amount         INTEGER DEFAULT 1
)
RETURNS BOOLEAN AS $$
DECLARE
    current_credits INTEGER;
BEGIN
    SELECT query_credits INTO current_credits FROM users WHERE id = target_user_id;
    IF current_credits IS NULL OR current_credits < amount THEN
        RETURN FALSE;
    END IF;
    UPDATE users SET query_credits = query_credits - amount WHERE id = target_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
