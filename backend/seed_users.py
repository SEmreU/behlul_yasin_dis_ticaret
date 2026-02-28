"""
Seed script — Test kullanıcılarını veritabanına ekler.
Kullanım: cd backend && python seed_users.py
"""
import sys
import os

# backend/ klasöründen çalıştırılacak
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, SubscriptionTier
from app.models.chatbot import ChatbotConfig, ChatbotConversation, ChatbotLead  # noqa
from app.models import UserActivity  # noqa

USERS = [
    {
        "email": "123@trade.com",
        "password": "123",
        "full_name": "Admin User 1",
        "is_superuser": True,
    },
    {
        "email": "1234@trade.com",
        "password": "1234",
        "full_name": "Admin User 2",
        "is_superuser": True,
    },
    {
        "email": "12345@trade.com",
        "password": "12345",
        "full_name": "Admin User 3",
        "is_superuser": True,
    },
]


def seed():
    db: Session = SessionLocal()
    try:
        for u in USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                # Şifreyi güncelle (hash'i yeniden üret)
                existing.hashed_password = get_password_hash(u["password"])
                existing.is_superuser = u["is_superuser"]
                existing.is_active = True
                print(f"✅ GÜNCELLENDI: {u['email']}")
            else:
                new_user = User(
                    email=u["email"],
                    hashed_password=get_password_hash(u["password"]),
                    full_name=u["full_name"],
                    is_superuser=u["is_superuser"],
                    is_active=True,
                    subscription_tier=SubscriptionTier.FREE,
                    query_credits=1000,
                )
                db.add(new_user)
                print(f"✅ EKLENDI: {u['email']}")
        db.commit()
        print("\n🎉 Tüm test kullanıcıları başarıyla eklendi!")
    except Exception as e:
        db.rollback()
        print(f"❌ HATA: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
