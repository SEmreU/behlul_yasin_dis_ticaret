# Yasin Dış Ticaret - Deployment Guide

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Docker & Docker Compose
- Node.js 20+ (local development)
- Python 3.12+ (local development)

### 1. Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env
# .env'i düzenle: DATABASE_URL, SECRET_KEY, API keys
```

### 2. Docker ile Başlat

```bash
# Tüm servisleri başlat
docker-compose up -d

# Logları izle
docker-compose logs -f

# Durdur
docker-compose down
```

**Servisler:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 3. Database Migration

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 4. İlk Kullanıcı Oluştur

```bash
# Register endpoint kullan
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yasin.com",
    "password": "admin12345",
    "full_name": "Admin User"
  }'
```

---

## 📦 Production Deployment

### Option 1: Railway (Kolay)

**Backend:**
1. Railway.app'e kayıt ol
2. New Project → Deploy from GitHub
3. PostgreSQL addon ekle
4. Environment variables ayarla
5. Deploy!

**Frontend:**
1. Vercel'e deploy (Next.js native)
2. Environment: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`

### Option 2: AWS/DigitalOcean (Manuel)

**Backend (EC2/Droplet):**
```bash
# Docker kurulu olmalı
git clone <repo>
cd yasin-dis-ticaret/backend
docker build -t yasin-backend .
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  yasin-backend
```

**Frontend (Vercel/Netlify):**
- GitHub repo bağla
- Auto-deploy aktif

### Option 3: Kubernetes (Advanced)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: yasin-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: yasin-backend
  template:
    metadata:
      labels:
        app: yasin-backend
    spec:
      containers:
      - name: backend
        image: yasin-backend:latest
        ports:
        - containerPort: 8000
```

---

## 🔒 Güvenlik Checklist

- [ ] `.env` dosyası `.gitignore`'da
- [ ] `SECRET_KEY` production'da değiştirildi
- [ ] HTTPS aktif (Let's Encrypt)
- [ ] CORS doğru ayarlandı
- [ ] Rate limiting aktif
- [ ] Database backups yapılandırıldı
- [ ] API keys güvenli saklanıyor
- [ ] Error logging (Sentry)

---

## 📊 Monitoring

### Sentry (Error Tracking)
```bash
pip install sentry-sdk
```

```python
import sentry_sdk
sentry_sdk.init(dsn="https://...")
```

### Uptime Monitoring
- UptimeRobot
- Pingdom
- StatusCake

---

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: vercel --prod
```

---

## 🐛 Troubleshooting

**Database connection error:**
```bash
# PostgreSQL çalışıyor mu?
docker ps | grep postgres
docker logs yasin-trade-postgres
```

**Frontend API bağlanamıyor:**
- CORS ayarlarını kontrol et
- `NEXT_PUBLIC_API_URL` doğru mu?

**Migration hatası:**
```bash
# Reset database (DEV ONLY!)
alembic downgrade base
alembic upgrade head
```

---

**Son Güncelleme:** 2026-02-06
