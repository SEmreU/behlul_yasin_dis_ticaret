# 🔄 Render + Supabase Hesap Devir Rehberi

> Yeni bir Supabase veya Render hesabına geçerken yapmanız gereken **minimum adımlar**.

---

## ÖNCELİK SIRASI

### ✅ KESİNLİKLE GEREKLI (olmadan çalışmaz)

| Dosya | Ne işe yarar |
|-------|-------------|
| [`render.yaml`](../render.yaml) | Render'ın projeyi nasıl deploy edeceğini tanımlar |
| [`supabase/migrations/001_initial_schema.sql`](../supabase/migrations/001_initial_schema.sql) | Tüm veritabanı tablolarını oluşturur |
| [`supabase/migrations/002_rls_policies.sql`](../supabase/migrations/002_rls_policies.sql) | Supabase güvenlik (RLS) katmanı |
| [`supabase/migrations/003_functions.sql`](../supabase/migrations/003_functions.sql) | `updated_at` trigger + arama+istatistik fonksiyonları |

---

### ⚠ ÇOK ÖNEMLİ ama olmasa da ilk başta çalışır

| Dosya | Ne işe yarar |
|-------|-------------|
| [`.env.example`](../.env.example) | Hangi değişkeni nereye gireceğinizi gösterir |
| [`supabase/seed.sql`](../supabase/seed.sql) | Admin kullanıcısı + örnek başlangıç verisi |

---

### 🔧 OPSİYONEL (kolaylık sağlar)

| Dosya | Ne işe yarar |
|-------|-------------|
| [`scripts/check_env.sh`](../scripts/check_env.sh) | Deploy öncesi ortam değişken kontrolü |
| [`scripts/setup.sh`](../scripts/setup.sh) | Tek seferlik kurulum scripti |
| [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) | Otomatik CI/CD pipeline |
| [`_KURULUM_REHBERI.md`](../_KURULUM_REHBERI.md) | Türkçe adım adım kurulum rehberi |
| [`supabase/config.toml`](../supabase/config.toml) | Sadece lokal Supabase CLI kullanılıyorsa |

---

## 3 ADIMDA DEVİR

### ADIM 1 — Supabase (yeni hesapta)

1. [supabase.com](https://supabase.com) → **New Project** → `yasin-trade`
2. **Settings → API** → URL ve key'leri kopyala
3. **Settings → Database → Connection string (Transaction, port 6543)** → kopyala
4. **SQL Editor'da sırayla çalıştır:**
   ```
   001_initial_schema.sql   ← Tablolar
   002_rls_policies.sql     ← Güvenlik
   003_functions.sql        ← Fonksiyonlar
   seed.sql                 ← Admin kullanıcısı (şifreyi değiştir!)
   ```

> ⚠ `seed.sql`'deki varsayılan admin şifresini mutlaka değiştirin:
> ```bash
> python3 -c "from passlib.hash import bcrypt; print(bcrypt.hash('YeniSifre123!'))"
> ```

---

### ADIM 2 — Render (yeni hesapta)

**Backend servisi için değiştirilecek env var'lar:**

| Değişken | Nereden alınır |
|----------|----------------|
| `DATABASE_URL` | Supabase → Settings → Database → Connection string |
| `FRONTEND_URL` | Render frontend servisinin URL'si |

> `render.yaml` dosyası repo'da olduğu için Render otomatik algılar.

**Frontend servisi için değiştirilecek env var:**

| Değişken | Değer |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Yeni Render backend URL'si |

---

### ADIM 3 — GitHub'a push

```bash
git push origin main
```

→ Render otomatik deploy tetiklenir.

---

## KONTROL LİSTESİ

```
[ ] Supabase yeni proje oluşturuldu
[ ] 3 migration SQL çalıştırıldı (001 → 002 → 003)
[ ] seed.sql çalıştırıldı + admin şifresi değiştirildi
[ ] Render backend'de DATABASE_URL güncellendi
[ ] Render backend'de FRONTEND_URL güncellendi
[ ] Render frontend'de NEXT_PUBLIC_API_URL güncellendi
[ ] GitHub'a push yapıldı
[ ] Backend health check: https://BACKEND.onrender.com/api/v1/health → 200 OK
[ ] Frontend açılıyor: https://FRONTEND.onrender.com
```

---

## ÖNEMLİ NOTLAR

- **`SECRET_KEY`** render.yaml'da `generateValue: true` olarak ayarlı → Render otomatik üretir, değiştirmek gerekmez
- **`.gitignore`** zaten `.env` satırını içeriyor → gerçek key'ler git'e gitmez
- **Free plan cold start:** İlk istekte 30-60 sn gecikme olabilir (Render uyku modundan uyanır)
- **Redis:** Celery background task'ları için gerekli. Render Redis veya [Upstash](https://upstash.com) (ücretsiz) kullanabilirsiniz

---

*Detaylı kurulum için: [_KURULUM_REHBERI.md](../_KURULUM_REHBERI.md)*
