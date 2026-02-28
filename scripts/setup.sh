#!/usr/bin/env bash
# ============================================================
# scripts/setup.sh — Tek Seferlik Kurulum Scripti
# Kullanım: chmod +x scripts/setup.sh && ./scripts/setup.sh
# ============================================================
set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${YELLOW}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[✅]${NC} $*"; }
fail()  { echo -e "${RED}[❌]${NC} $*"; }
line()  { echo -e "─────────────────────────────────────────────"; }

line
echo " 🚀  Yasin Dış Ticaret — Kurulum Başlatıldı"
line

# ─── 1. .env dosyası kontrol ────────────────────────────────
info "1/6 → .env dosyası kontrol ediliyor..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        ok ".env.example → .env kopyalandı. Lütfen değerleri doldurun!"
        fail "Devam etmeden önce .env dosyasını düzenleyin."
        exit 1
    else
        fail ".env ve .env.example bulunamadı!"
        exit 1
    fi
else
    ok ".env mevcut"
fi

# .env yükle
set -a
source .env
set +a

# ─── 2. Zorunlu env var kontrolü ────────────────────────────
info "2/6 → Zorunlu değişkenler kontrol ediliyor..."
MISSING=()
REQUIRED_VARS=("DATABASE_URL" "SECRET_KEY" "FRONTEND_URL")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        MISSING+=("$var")
    fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
    fail "Eksik zorunlu değişkenler: ${MISSING[*]}"
    echo "   .env dosyasında bu değişkenleri doldurun."
    exit 1
fi
ok "Zorunlu değişkenler tanımlı"

# ─── 3. Python / virtual env ────────────────────────────────
info "3/6 → Python ortamı kontrol ediliyor..."
if [ -d "backend/venv" ]; then
    ok "Virtual env mevcut (backend/venv)"
    PYTHON="backend/venv/bin/python"
else
    info "Virtual env oluşturuluyor..."
    python3 -m venv backend/venv
    ok "Virtual env oluşturuldu"
    PYTHON="backend/venv/bin/python"
fi

$PYTHON -m pip install --quiet --upgrade pip
$PYTHON -m pip install --quiet -r backend/requirements.txt
ok "Python bağımlılıkları kuruldu"

# ─── 4. Node.js bağımlılıkları ──────────────────────────────
info "4/6 → Node.js bağımlılıkları kuruluyor..."
(cd frontend && npm install --silent)
ok "Node.js bağımlılıkları kuruldu"

# ─── 5. Supabase migration'ları ─────────────────────────────
info "5/6 → Supabase migration talimatları..."
echo ""
echo "  📋 Supabase SQL Editor'da sırayla çalıştırın:"
echo "     1. supabase/migrations/001_initial_schema.sql"
echo "     2. supabase/migrations/002_rls_policies.sql"
echo "     3. supabase/migrations/003_functions.sql"
echo "     4. supabase/seed.sql (opsiyonel — test verisi)"
echo ""
echo "  ⚠  seed.sql'deki admin şifresini değiştirin!"
echo ""

# Supabase CLI varsa otomatik çalıştır
if command -v supabase &>/dev/null; then
    info "Supabase CLI bulundu — migration'lar uygulanıyor..."
    supabase db push --db-url "$DATABASE_URL" <<'MIGRATION'
\i supabase/migrations/001_initial_schema.sql
\i supabase/migrations/002_rls_policies.sql
\i supabase/migrations/003_functions.sql
MIGRATION
    ok "Supabase migration'ları tamamlandı"
else
    info "Supabase CLI kurulu değil — manuel çalıştırın (yukarıdaki adımlar)"
fi

# ─── 6. Build testi ─────────────────────────────────────────
info "6/6 → Frontend build testi yapılıyor..."
(cd frontend && npm run build --silent)
ok "Frontend build başarılı"

line
ok "Kurulum tamamlandı!"
echo ""
echo "  Sonraki adımlar:"
echo "  1. Supabase migration'larını çalıştırın (adım 5)"
echo "  2. render.yaml'deki tüm env var'ları Render paneline girin"
echo "  3. GitHub'a push yapın → Render otomatik deploy eder"
echo ""
echo "  Backend yerel başlatma:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "  Frontend yerel başlatma:"
echo "  cd frontend && npm run dev"
line
