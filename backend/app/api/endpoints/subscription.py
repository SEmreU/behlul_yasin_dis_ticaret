"""Subscription & Payment Management"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, SubscriptionTier

router = APIRouter()


class SubscriptionUpgradeRequest(BaseModel):
    tier: str  # "pro" or "enterprise"
    payment_method_id: Optional[str] = None  # Stripe payment method ID


@router.get("/plans")
def get_subscription_plans():
    """
    Abonelik planları ve fiyatları

    Free, Pro, Enterprise tier özellikleri
    """
    return {
        "plans": [
            {
                "tier": "free",
                "name": "Free",
                "price": 0,
                "currency": "USD",
                "credits_per_month": 10,
                "features": [
                    "10 aylık sorgu",
                    "1 mail kampanyası",
                    "Temel dashboard"
                ]
            },
            {
                "tier": "pro",
                "name": "Professional",
                "price": 49,
                "currency": "USD",
                "credits_per_month": 1000,
                "features": [
                    "1000 aylık sorgu",
                    "Unlimited mail kampanyaları",
                    "Tüm modüller",
                    "Priority support",
                    "Export to Excel"
                ]
            },
            {
                "tier": "enterprise",
                "name": "Enterprise",
                "price": 199,
                "currency": "USD",
                "credits_per_month": 999999,
                "features": [
                    "Unlimited sorgu",
                    "Custom integrations",
                    "Dedicated account manager",
                    "White-label option",
                    "API access"
                ]
            }
        ]
    }


@router.post("/upgrade")
def upgrade_subscription(
    request: SubscriptionUpgradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Abonelik yükselt

    Stripe entegrasyonu ile ödeme işlemi

    Args:
        tier: "pro" or "enterprise"
        payment_method_id: Stripe payment method ID

    Flow:
    1. Stripe customer oluştur (ilk kez)
    2. Payment method attach et
    3. Subscription oluştur
    4. Webhook ile confirmation bekle
    5. User tier'ı güncelle
    """
    if request.tier not in ["pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid tier")

    # TODO: Stripe entegrasyonu
    # import stripe
    # stripe.api_key = settings.STRIPE_SECRET_KEY
    #
    # # Customer oluştur veya al
    # customer = stripe.Customer.create(
    #     email=current_user.email,
    #     payment_method=request.payment_method_id,
    #     invoice_settings={"default_payment_method": request.payment_method_id}
    # )
    #
    # # Subscription oluştur
    # price_id = "price_pro" if request.tier == "pro" else "price_enterprise"
    # subscription = stripe.Subscription.create(
    #     customer=customer.id,
    #     items=[{"price": price_id}],
    #     expand=["latest_invoice.payment_intent"]
    # )

    # Şimdilik direkt tier güncelle (mock)
    if request.tier == "pro":
        current_user.subscription_tier = SubscriptionTier.PRO
        current_user.query_credits = 1000
    elif request.tier == "enterprise":
        current_user.subscription_tier = SubscriptionTier.ENTERPRISE
        current_user.query_credits = 999999

    db.commit()

    return {
        "message": f"Subscription upgraded to {request.tier}",
        "new_tier": current_user.subscription_tier,
        "credits": current_user.query_credits
    }


@router.post("/cancel")
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Aboneliği iptal et

    Dönem sonunda FREE tier'a düşer
    """
    # TODO: Stripe subscription cancel
    # stripe.Subscription.delete(subscription_id)

    current_user.subscription_tier = SubscriptionTier.FREE
    current_user.query_credits = 10
    db.commit()

    return {
        "message": "Subscription cancelled. You will be downgraded to FREE at the end of billing period.",
        "new_tier": "free"
    }


@router.post("/webhook/stripe")
async def stripe_webhook():
    """
    Stripe webhook endpoint

    Events:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    """
    # TODO: Stripe webhook signature verification
    # import stripe
    # event = stripe.Webhook.construct_event(
    #     payload, sig_header, endpoint_secret
    # )

    return {"received": True}
