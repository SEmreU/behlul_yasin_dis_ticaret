from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.endpoints import (
    health, auth, visitor, search, scraping, campaigns, 
    analytics, gdpr, subscription, maps, b2b, contact, 
    chatbot, fairs, markets, admin, marketplace
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


@app.on_event("startup")
def on_startup():
    """Create all database tables on startup"""
    init_db()


# CORS
allowed_origins = ["http://localhost:3000", "http://localhost:3001"]
if settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(visitor.router, prefix=f"{settings.API_V1_STR}/visitor", tags=["visitor-tracking"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["product-search"])
app.include_router(scraping.router, prefix=f"{settings.API_V1_STR}/scraping", tags=["scraping"])
app.include_router(campaigns.router, prefix=f"{settings.API_V1_STR}/campaigns", tags=["email-campaigns"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["analytics"])
app.include_router(gdpr.router, prefix=f"{settings.API_V1_STR}/gdpr", tags=["gdpr-kvkk"])
app.include_router(subscription.router, prefix=f"{settings.API_V1_STR}/subscription", tags=["subscription"])

# New TradeRadar Module Routes
app.include_router(maps.router, prefix=f"{settings.API_V1_STR}/maps", tags=["maps-research"])
app.include_router(b2b.router, prefix=f"{settings.API_V1_STR}/b2b", tags=["b2b-platforms"])
app.include_router(contact.router, prefix=f"{settings.API_V1_STR}/contact", tags=["contact-finder"])
app.include_router(chatbot.router, prefix=f"{settings.API_V1_STR}/chatbot", tags=["ai-chatbot"])
app.include_router(fairs.router, prefix=f"{settings.API_V1_STR}/fairs", tags=["fair-analysis"])
app.include_router(markets.router, prefix=f"{settings.API_V1_STR}/markets", tags=["market-research"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin-settings"])
app.include_router(marketplace.router, prefix=f"{settings.API_V1_STR}/marketplace", tags=["marketplace"])


@app.get("/")
async def root():
    return {
        "message": "Yasin Dış Ticaret İstihbarat API",
        "version": settings.VERSION,
        "docs": "/docs"
    }
