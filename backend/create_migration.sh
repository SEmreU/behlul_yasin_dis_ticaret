#!/bin/bash
# İlk migration oluştur

source venv/bin/activate
export DATABASE_URL="postgresql://yasin:yasin123@localhost:5432/yasin_trade_db"

alembic revision --autogenerate -m "Initial database schema"
echo "Migration oluşturuldu!"
echo "Uygulamak için: alembic upgrade head"
