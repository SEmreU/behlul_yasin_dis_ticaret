# 🚀 Yasin Dış Ticaret — Sıfırdan Kurulum Rehberi

> **Tahmini kurulum süresi:** 30-45 dakika  
> **Ön koşul:** GitHub hesabı, Supabase hesabı, Render hesabı

---

## İÇİNDEKİLER

1. [Supabase Kurulumu](#1-supabase-kurulumu)
2. [Render Kurulumu](#2-render-kurulumu)
3. [GitHub Secrets Kurulumu](#3-github-secrets-kurulumu)
4. [İlk Deploy ve Test](#4-ilk-deploy-ve-test)
5. [Admin Hesabı ve İlk Giriş](#5-admin-hesabı-ve-ilk-giriş)
6. [Önemli Uyarılar](#6-önemli-uyarılar)

---

## 1. SUPABASE KURULUMU

### 1.1 Yeni Proje Oluştur
1. [supabase.com](https://supabase.com) → **New Project** tıklayın
2. Organization seçin → Proje adı: `yasin-trade`
3. Şifre oluşturun (güçlü bir şifre — sonra lazım!)
4. Bölge: **EU Central (Frankfurt)** önerilen (Türkiye'ye yakın)
5. **Create new project** → ~2 dakika bekleyin

### 1.2 API Bilgilerini Alın
1. Sol menü → **Settings** → **API**
2. Kopyalayın:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon/public key** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_SERVICE_ROLE_KEY` ⚠ SAKLAYIN, paylaşmayın

### 1.3 Veritabanı Bağlantı Stringini Alın
1. Sol menü → **Settings** → **Database**
2. **Connection string** bölümü → **Transaction** sekmesini seçin (port 6543)
3. URI'yi kopyalayın → `DATABASE_URL` değişkeni için kullanın
4. `[YOUR-PASSWORD]` yerine adım 1.1'deki şifreyi yazın

### 1.4 SQL Migration'ları Çalıştırın
**SQL Editor** → **New query** → Sırayla çalıştırın:

```
Adım 1: supabase/migrations/001_initial_schema.sql ← Tablolar
Adım 2: supabase/migrations/002_rls_policies.sql   ← Güvenlik
Adım 3: supabase/migrations/003_functions.sql      ← Fonksiyonlar
Adım 4: supabase/seed.sql                          ← İlk veriler
```

> ⚠ **seed.sql çalıştırmadan önce:** Admin şifresini değiştirin!
> ```bash
> python3 -c "from passlib.hash import bcrypt; print(bcrypt.hash('YeniSifreniz123!'))"
> ```
> Çıkan hash'i seed.sql'deki `hashed_password` alanına yazın.

### 1.5 Storage Kurulumu (İsteğe bağlı)
1. Sol menü → **Storage** → **New bucket**
2. Bucket adı: `company-files`
3. Public: ❌ Kapalı

---

## 2. RENDER KURULUMU

### 2.1 Backend Servisi

1. [render.com](https://render.com) → **New +** → **Web Service**
2. **Connect a repository** → GitHub reposunu bağlayın
3. Ayarlar:
   | Alan | Değer |
   |------|-------|
   | Name | `yasin-trade-backend` |
   | Region | Frankfurt (EU) |
   | Branch | `main` |
   | Root Directory | `backend` |
   | Runtime | `Python` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | Free (başlangıç için) |

4. **Environment Variables** bölümüne gidin (sonraki adım)

### 2.2 Backend Environment Variables
Aşağıdaki değişkenleri **zorunlu olarak** girin:

| Değişken | Değer |
|----------|-------|
| `DATABASE_URL` | Supabase Transaction connection string |
| `SECRET_KEY` | Render otomatik üretir (generateValue: true) |
| `FRONTEND_URL` | `https://yasin-trade-frontend.onrender.com` |
| `ENVIRONMENT` | `production` |
| `GROQ_API_KEY` | Groq API key (ücretsiz) |
| `SCRAPERAPI_KEY` | ScraperAPI key |

Diğer opsiyonel değişkenler için `.env.example` dosyasına bakın.

### 2.3 Frontend Servisi

1. **New +** → **Web Service**
2. Aynı GitHub reposunu seçin
3. Ayarlar:
   | Alan | Değer |
   |------|-------|
   | Name | `yasin-trade-frontend` |
   | Root Directory | `frontend` |
   | Runtime | `Node` |
   | Build Command | `npm install && npm run build` |
   | Start Command | `npm start` |

4. Environment Variables:
   | Değişken | Değer |
   |----------|-------|
   | `NEXT_PUBLIC_API_URL` | `https://yasin-trade-backend.onrender.com` |
   | `NODE_ENV` | `production` |

### 2.4 Redis (Background Tasks)

**Seçenek A — Render Redis:**
1. **New +** → **Redis** → Oluşturun
2. Internal URL'yi kopyalayın → Backend'de `REDIS_URL` olarak ekleyin

**Seçenek B — Upstash Redis (ücretsiz):**
1. [upstash.com](https://upstash.com) → Redis → Create Database
2. URL'yi → `REDIS_URL` olarak girin

> ⚠ Redis olmadan Celery background task'ları çalışmaz. Email kampanyaları etkilenir.

---

## 3. GITHUB SECRETS KURULUMU

GitHub Actions'ın çalışması için repo'ya secret ekleyin:

1. GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** ile her birini ekleyin:

| Secret Adı | Değer |
|-----------|-------|
| `DATABASE_URL` | Supabase connection string |
| `SECRET_KEY` | Güçlü rastgele string |
| `FRONTEND_URL` | Frontend URL'si |
| `SUPABASE_DB_URL` | Supabase DB URL (migration için) |
| `NEXT_PUBLIC_API_URL` | Backend URL'si |
| `NEXT_PUBLIC_APP_URL` | Frontend URL'si |

---

## 4. İLK DEPLOY VE TEST

### 4.1 Deploy Tetikleme
```bash
git add .
git commit -m "feat: production deployment configuration"
git push origin main
```

GitHub Actions otomatik çalışır → Render otomatik deploy alır.

### 4.2 Deploy Durumunu Takip Edin
- **GitHub Actions:** `https://github.com/KULLANICI/repo/actions`
- **Render Backend:** `https://dashboard.render.com`

> ⏱ İlk deploy ~5-10 dakika sürebilir. Free plan'da ilk istek 30-60 saniye bekleyebilir (cold start).

### 4.3 Test Edin
Tarayıcıda açın:
```
Backend API Docs:  https://yasin-trade-backend.onrender.com/docs
Backend Health:    https://yasin-trade-backend.onrender.com/api/v1/health
Frontend:         https://yasin-trade-frontend.onrender.com
```

Çalışma kontrol scripti:
```bash
./scripts/check_env.sh
```

---

## 5. ADMIN HESABI VE İLK GİRİŞ

### 5.1 Admin Şifresi Oluşturun
```bash
cd backend
source venv/bin/activate
python3 -c "from passlib.hash import bcrypt; print(bcrypt.hash('GucluSifre123!'))"
```

### 5.2 Admin Kullanıcı Ekleyin
Supabase SQL Editor'da:
```sql
INSERT INTO users (email, hashed_password, full_name, subscription_tier, query_credits, is_active, is_admin)
VALUES (
    'sizin@email.com',
    'YUKARIDAKI_HASH',   -- 5.1'de üretilen hash
    'Ad Soyad',
    'ENTERPRISE',
    99999,
    TRUE,
    TRUE
);
```

### 5.3 Admin Paneli
Frontend URL'ye gidin → Login → Admin paneline erişin:
- API key'leri admin panelden girebilirsiniz
- Kullanıcı yönetimi, kampanyalar, analytics burada

---

## 6. ÖNEMLİ UYARILAR

> [!CAUTION]
> **seed.sql'deki varsayılan admin şifresi production'da kullanmayın!**
> Mutlaka yeni hash ile güncelleyin.

> [!WARNING]
> **`SUPABASE_SERVICE_ROLE_KEY`** backend'de güvenle kullanılır.
> Frontend'e asla göndermeyın (`.env` → git'e eklemeyin).

> [!IMPORTANT]
> **`.gitignore`** dosyasında `.env` satırının olduğunu doğrulayın:
> ```bash
> grep ".env" .gitignore
> ```

> [!NOTE]
> **Render Free Plan cold start:** İlk istekte 30-60 sn gecikme olabilir.
> Sürekli çalışması için paid plan veya UptimeRobot ile ping kurabilirsiniz.

---

## HIZLI BAŞVURU

```bash
# Yerel geliştirme
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

cd frontend && npm run dev

# Ortam kontrolü
./scripts/check_env.sh

# Kurulum (sıfırdan)
./scripts/setup.sh
```

**Destek:** Sorunlar için `_render_setup.md` ve Render logs bölümünü inceleyin.
