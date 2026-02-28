#!/usr/bin/env bash
# ============================================================
# scripts/check_env.sh — Deploy öncesi ortam değişkeni kontrolü
# Kullanım: ./scripts/check_env.sh
# ============================================================
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ok()   { echo -e "${GREEN}  ✅  $*${NC}"; }
fail() { echo -e "${RED}  ❌  $*${NC}"; ERRORS=$((ERRORS + 1)); }
warn() { echo -e "${YELLOW}  ⚠   $*${NC}"; }
info() { echo -e "${BLUE}  →   $*${NC}"; }

ERRORS=0

echo ""
echo "════════════════════════════════════════════"
echo "  Yasin Dış Ticaret — Ortam Değişken Kontrolü"
echo "════════════════════════════════════════════"
echo ""

# .env dosyasını yükle (varsa)
if [ -f ".env" ]; then
    set -a; source .env; set +a
    info ".env dosyası yüklendi"
elif [ -f "backend/.env" ]; then
    set -a; source backend/.env; set +a
    info "backend/.env dosyası yüklendi"
else
    warn ".env dosyası bulunamadı — sistem ortam değişkenleri kontrol edilecek"
fi

echo ""
info "── ZORUNLU DEĞİŞKENLER ──────────────────────"

# Database
if [ -n "${DATABASE_URL:-}" ]; then
    ok "DATABASE_URL tanımlı"
else
    fail "DATABASE_URL eksik! (Supabase > Settings > Database > Connection string)"
fi

# Security
if [ -n "${SECRET_KEY:-}" ] && [ ${#SECRET_KEY} -ge 32 ]; then
    ok "SECRET_KEY tanımlı (${#SECRET_KEY} karakter)"
elif [ -n "${SECRET_KEY:-}" ]; then
    fail "SECRET_KEY çok kısa! En az 32 karakter olmalı."
else
    fail "SECRET_KEY eksik!"
fi

# Frontend URL
if [ -n "${FRONTEND_URL:-}" ] || [ -n "${NEXT_PUBLIC_API_URL:-}" ]; then
    ok "Frontend/API URL tanımlı"
else
    fail "FRONTEND_URL veya NEXT_PUBLIC_API_URL eksik!"
fi

echo ""
info "── AI SAĞLAYICILARI (En az biri zorunlu) ───"

AI_COUNT=0
[ -n "${GROQ_API_KEY:-}" ]        && { ok "GROQ_API_KEY tanımlı ✨ (önerilen)"; AI_COUNT=$((AI_COUNT+1)); }
[ -n "${OPENAI_API_KEY:-}" ]      && { ok "OPENAI_API_KEY tanımlı"; AI_COUNT=$((AI_COUNT+1)); }
[ -n "${ANTHROPIC_API_KEY:-}" ]   && { ok "ANTHROPIC_API_KEY tanımlı"; AI_COUNT=$((AI_COUNT+1)); }
[ -n "${HUGGINGFACE_API_KEY:-}" ] && { ok "HUGGINGFACE_API_KEY tanımlı"; AI_COUNT=$((AI_COUNT+1)); }
if [ $AI_COUNT -eq 0 ]; then
    fail "Hiç AI API key tanımlı değil! Chatbot ve AI özellikler çalışmaz."
fi

echo ""
info "── OPSİYONEL API'LER ────────────────────────"

[ -n "${GOOGLE_MAPS_API_KEY:-}" ] && ok "GOOGLE_MAPS_API_KEY" || warn "GOOGLE_MAPS_API_KEY eksik (Harita modülü pasif)"
[ -n "${SCRAPERAPI_KEY:-}" ]      && ok "SCRAPERAPI_KEY"      || warn "SCRAPERAPI_KEY eksik (B2B scraping sınırlı)"
[ -n "${SENDGRID_API_KEY:-}" ] || [ -n "${RESEND_API_KEY:-}" ] || [ -n "${SMTP_HOST:-}" ] \
    && ok "Email servisi tanımlı" \
    || warn "Email servisi yok (SENDGRID/RESEND/SMTP — mail gönderimi pasif)"
[ -n "${REDIS_URL:-}" ] && ok "REDIS_URL" || warn "REDIS_URL eksik (Background task'lar pasif)"
[ -n "${GOOGLE_CLIENT_ID:-}" ]    && ok "GOOGLE_CLIENT_ID (OAuth)" || warn "GOOGLE_CLIENT_ID eksik (Google Login pasif)"

echo ""
info "── SUPABASE BAĞLANTI TESTİ ─────────────────"
if [ -n "${DATABASE_URL:-}" ]; then
    if command -v psql &>/dev/null; then
        if psql "${DATABASE_URL}" -c "SELECT 1" &>/dev/null 2>&1; then
            ok "Supabase veritabanı bağlantısı başarılı!"
        else
            fail "Supabase bağlantısı başarısız! DATABASE_URL'yi kontrol edin."
        fi
    else
        warn "psql kurulu değil, DB bağlantı testi atlandı"
    fi
fi

info "── SCRAPERAPI TESTİ ─────────────────────────"
if [ -n "${SCRAPERAPI_KEY:-}" ]; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        "https://api.scraperapi.com/?api_key=${SCRAPERAPI_KEY}&url=https://httpbin.org/get" \
        --max-time 10 2>/dev/null || echo "000")
    if [ "$HTTP_STATUS" = "200" ]; then
        ok "ScraperAPI bağlantısı başarılı!"
    else
        warn "ScraperAPI testi başarısız (HTTP: $HTTP_STATUS) — key geçersiz veya limit aşıldı"
    fi
else
    warn "SCRAPERAPI_KEY tanımlı değil, test atlandı"
fi

echo ""
echo "════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}  ✅  Tüm kontroller geçti! Deploy'a hazır.${NC}"
else
    echo -e "${RED}  ❌  $ERRORS hata var! Deploy öncesi düzeltin.${NC}"
    exit 1
fi
echo "════════════════════════════════════════════"
echo ""
