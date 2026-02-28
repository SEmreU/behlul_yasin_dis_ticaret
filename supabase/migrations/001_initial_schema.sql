-- ============================================================
-- 001_initial_schema.sql
-- Yasin Dış Ticaret — Supabase İlk Şema
-- Çalıştırma: Supabase Dashboard > SQL Editor > Run
-- ============================================================

-- Gerekli extension'lar
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- full-text trigram arama

-- ── Enum Tipleri ─────────────────────────────────────────────

CREATE TYPE subscription_tier AS ENUM ('FREE', 'PRO', 'ENTERPRISE');
CREATE TYPE query_type        AS ENUM ('product_search', 'map_scraping', 'fair_search', 'image_search', 'b2b_search', 'contact_search');
CREATE TYPE query_status      AS ENUM ('pending', 'completed', 'failed');
CREATE TYPE campaign_status   AS ENUM ('draft', 'scheduled', 'sending', 'completed', 'paused');


-- ── 1. USERS ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email                    TEXT NOT NULL UNIQUE,
    hashed_password          TEXT,                          -- NULL = OAuth kullanıcı
    full_name                TEXT,
    subscription_tier        subscription_tier NOT NULL DEFAULT 'FREE',
    query_credits            INTEGER NOT NULL DEFAULT 50,    -- Aylık sorgu hakkı
    is_active                BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin                 BOOLEAN NOT NULL DEFAULT FALSE,
    google_id                TEXT UNIQUE,                   -- Google OAuth
    avatar_url               TEXT,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email        ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_tier);
CREATE INDEX IF NOT EXISTS idx_users_google_id    ON users(google_id) WHERE google_id IS NOT NULL;


-- ── 2. COMPANIES ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS companies (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name           TEXT NOT NULL,
    country        TEXT,
    city           TEXT,
    address        TEXT,
    website        TEXT,
    phone          TEXT,
    email          TEXT,
    contact_emails JSONB DEFAULT '[]'::JSONB,   -- ["purchasing@...", "sales@..."]
    latitude       DOUBLE PRECISION,
    longitude      DOUBLE PRECISION,
    source         TEXT,                         -- google_maps, alibaba, fair, manual
    metadata       JSONB DEFAULT '{}'::JSONB,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_companies_name    ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_country ON companies(country);
CREATE INDEX IF NOT EXISTS idx_companies_source  ON companies(source);
-- Trigram index for fuzzy name search
CREATE INDEX IF NOT EXISTS idx_companies_name_trgm ON companies USING gin(name gin_trgm_ops);


-- ── 3. PRODUCTS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gtip_code    TEXT,                              -- GTIP / HS code
    oem_code     TEXT,                              -- OEM / Part number
    descriptions JSONB DEFAULT '{}'::JSONB,         -- {"tr": "...", "en": "...", "de": "..."}
    category     TEXT,
    subcategory  TEXT,
    image_url    TEXT,
    metadata     JSONB DEFAULT '{}'::JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_gtip ON products(gtip_code);
CREATE INDEX IF NOT EXISTS idx_products_oem  ON products(oem_code);


-- ── 4. SEARCH_QUERIES ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS search_queries (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id          UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query_type       query_type NOT NULL,
    query_parameters JSONB DEFAULT '{}'::JSONB,
    results_count    INTEGER DEFAULT 0,
    results_data     JSONB DEFAULT '[]'::JSONB,     -- Preview data
    credits_used     INTEGER DEFAULT 1,
    status           query_status NOT NULL DEFAULT 'pending',
    error_message    TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_search_user    ON search_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_search_type    ON search_queries(query_type);
CREATE INDEX IF NOT EXISTS idx_search_created ON search_queries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_search_status  ON search_queries(status);


-- ── 5. VISITOR_IDENTIFICATIONS ───────────────────────────────
CREATE TABLE IF NOT EXISTS visitor_identifications (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id                  TEXT UNIQUE,
    ip_address                  TEXT,
    user_agent                  TEXT,
    referer                     TEXT,
    latitude                    DOUBLE PRECISION,
    longitude                   DOUBLE PRECISION,
    location_source             TEXT DEFAULT 'ip_geolocation', -- gps | ip_geolocation
    identified_company_id       UUID REFERENCES companies(id) ON DELETE SET NULL,
    confidence_score            DOUBLE PRECISION DEFAULT 0,    -- 0.0 - 1.0
    browser_fingerprint         TEXT,
    location_permission_granted BOOLEAN DEFAULT FALSE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_visitor_ip      ON visitor_identifications(ip_address);
CREATE INDEX IF NOT EXISTS idx_visitor_session ON visitor_identifications(session_id);
CREATE INDEX IF NOT EXISTS idx_visitor_company ON visitor_identifications(identified_company_id);
CREATE INDEX IF NOT EXISTS idx_visitor_created ON visitor_identifications(created_at DESC);


-- ── 6. EMAIL_CAMPAIGNS ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS email_campaigns (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    subject             TEXT,
    body_template       TEXT,
    target_company_ids  JSONB DEFAULT '[]'::JSONB,
    target_filters      JSONB DEFAULT '{}'::JSONB,
    attachments         JSONB DEFAULT '[]'::JSONB,  -- [{"name": "catalog.pdf", "url": "..."}]
    total_recipients    INTEGER DEFAULT 0,
    sent_count          INTEGER DEFAULT 0,
    opened_count        INTEGER DEFAULT 0,
    clicked_count       INTEGER DEFAULT 0,
    bounced_count       INTEGER DEFAULT 0,
    status              campaign_status NOT NULL DEFAULT 'draft',
    scheduled_at        TIMESTAMPTZ,
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaign_user   ON email_campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_campaign_status ON email_campaigns(status);


-- ── 7. CAMPAIGN_EMAILS ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS campaign_emails (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id          UUID NOT NULL REFERENCES email_campaigns(id) ON DELETE CASCADE,
    company_id           UUID REFERENCES companies(id) ON DELETE SET NULL,
    recipient_email      TEXT NOT NULL,
    recipient_name       TEXT,
    personalized_subject TEXT,
    personalized_body    TEXT,
    tracking_id          TEXT UNIQUE DEFAULT gen_random_uuid()::TEXT,
    is_sent              BOOLEAN DEFAULT FALSE,
    is_opened            BOOLEAN DEFAULT FALSE,
    is_clicked           BOOLEAN DEFAULT FALSE,
    is_bounced           BOOLEAN DEFAULT FALSE,
    sent_at              TIMESTAMPTZ,
    opened_at            TIMESTAMPTZ,
    clicked_at           TIMESTAMPTZ,
    bounced_at           TIMESTAMPTZ,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_campaign  ON campaign_emails(campaign_id);
CREATE INDEX IF NOT EXISTS idx_email_tracking  ON campaign_emails(tracking_id);
CREATE INDEX IF NOT EXISTS idx_email_company   ON campaign_emails(company_id);


-- ── 8. FAIR_EXHIBITORS ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS fair_exhibitors (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fair_name           TEXT NOT NULL,
    fair_location       TEXT,
    fair_date           DATE,
    company_name        TEXT NOT NULL,
    booth_number        TEXT,
    hall                TEXT,
    country             TEXT,
    city                TEXT,
    website             TEXT,
    email               TEXT,
    phone               TEXT,
    product_categories  JSONB DEFAULT '[]'::JSONB,
    product_description TEXT,
    match_score         INTEGER DEFAULT 0,          -- 0-100 eşleşme skoru
    matched_keywords    JSONB DEFAULT '[]'::JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fair_name    ON fair_exhibitors(fair_name);
CREATE INDEX IF NOT EXISTS idx_fair_country ON fair_exhibitors(country);
CREATE INDEX IF NOT EXISTS idx_fair_date    ON fair_exhibitors(fair_date);


-- ── 9. USER_ACTIVITY (Admin paneli için) ─────────────────────
CREATE TABLE IF NOT EXISTS user_activity (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    module     TEXT,                 -- 'b2b', 'search', 'maps', 'chatbot' vb.
    action     TEXT,                 -- 'search', 'export', 'view' vb.
    detail     JSONB DEFAULT '{}'::JSONB,
    ip_address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_user    ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_module  ON user_activity(module);
CREATE INDEX IF NOT EXISTS idx_activity_created ON user_activity(created_at DESC);
