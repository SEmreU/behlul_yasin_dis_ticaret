#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError

users = [
    {"email": "123@trade.com",    "password": "123",    "full_name": "Test User 1"},
    {"email": "1234@trade.com",   "password": "1234",   "full_name": "Test User 2"},
    {"email": "12345@trade.com",  "password": "12345",  "full_name": "Test User 3"},
    {"email": "123456@trade.com", "password": "123456", "full_name": "Test User 4"},
]

db = SessionLocal()
try:
    for u in users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            print(f"⚠️  Zaten mevcut: {u['email']}")
            continue
        user = User(
            email=u["email"],
            hashed_password=get_password_hash(u["password"]),
            full_name=u["full_name"],
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        try:
            db.commit()
            print(f"✅ Eklendi: {u['email']}")
        except IntegrityError:
            db.rollback()
            print(f"❌ Hata: {u['email']} eklenirken IntegrityError")
finally:
    db.close()
    print("\nTamamlandı.")
