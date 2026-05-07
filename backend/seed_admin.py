"""
Seed script: creates the initial admin user.
Run: python seed_admin.py

Reads credentials from environment variables:
  ADMIN_USERNAME  (default: admin)
  ADMIN_PASSWORD  (default: changeme-admin)

Idempotent: does nothing if the admin user already exists.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("DATABASE_URL", "sqlite:///./quiniela.db")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User
from app.auth import hash_password

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quiniela.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme-admin")


def seed(db) -> bool:
    existing = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    if existing:
        print(f"⚠️  User '{ADMIN_USERNAME}' already exists (status={existing.status}). Skipping.")
        return False

    admin = User(
        username=ADMIN_USERNAME,
        password_hash=hash_password(ADMIN_PASSWORD),
        is_admin=1,
        status="Active",
    )
    db.add(admin)
    db.commit()
    return True


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        created = seed(db)
        if created:
            print(f"✅ Admin user '{ADMIN_USERNAME}' created with status=Active, is_admin=1.")
            print("   Change the password before going to production!")
    finally:
        db.close()
