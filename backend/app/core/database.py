from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """Import all models and create tables"""
    # Import all models so they are registered with Base
    from app.models import (  # noqa: F401
        User, Company, Product, SearchQuery,
        VisitorIdentification, EmailCampaign, CampaignEmail,
        FairExhibitor, ApiSetting
    )
    Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
