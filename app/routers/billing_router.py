import secrets
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, SubscriptionInvoice, TokenUsageLog
from ..auth import get_current_user

router = APIRouter(prefix="/api/billing", tags=["Billing & Subscriptions"])

SUBSCRIPTION_PLANS = {
    "starter": {
        "id": "starter",
        "name": "Freelance Starter",
        "price_monthly": 29.0,
        "tokens_included": 100000,
        "features": [
            "Up to 100k AI Tokens / month",
            "Unlimited Client Projects",
            "4 Diplomatic Response Tones",
            "PDF/Markdown Addendum Export",
            "Single User Seat"
        ]
    },
    "pro": {
        "id": "pro",
        "name": "Studio Pro",
        "price_monthly": 79.0,
        "tokens_included": 500000,
        "features": [
            "500k AI Tokens / month",
            "Priority AI Reasoning Engine",
            "Custom Hourly Rates & Margins",
            "Team Collaboration (Up to 5 seats)",
            "Stripe Invoice Checkout Links",
            "Historical FinOps Cost Audit"
        ]
    },
    "agency": {
        "id": "agency",
        "name": "Agency Scale",
        "price_monthly": 199.0,
        "tokens_included": 2000000,
        "features": [
            "2,000,000 AI Tokens / month",
            "Unlimited Team Seats",
            "Custom Legal Clauses & White-label",
            "Bring Your Own API Keys (BYOK)",
            "Dedicated Slack/Webhook Alerts",
            "1-on-1 Agency Onboarding"
        ]
    }
}

class SubscribeRequest(BaseModel):
    plan_tier: str  # 'starter', 'pro', 'agency'
    payment_method: Optional[str] = "Visa ending in 4242"
    billing_cycle: Optional[str] = "monthly"

@router.get("/plans")
def list_plans():
    return list(SUBSCRIPTION_PLANS.values())

@router.get("/usage")
def get_usage(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = SUBSCRIPTION_PLANS.get(user.plan_tier, SUBSCRIPTION_PLANS["pro"])
    
    # Calculate all-time token stats
    token_logs = db.query(TokenUsageLog).filter(TokenUsageLog.user_id == user.id).all()
    all_time_tokens = sum(log.total_tokens for log in token_logs)
    all_time_cost = sum(log.cost_usd for log in token_logs)

    usage_percent = round((user.monthly_tokens_used / max(1, user.monthly_token_quota)) * 100, 1)

    return {
        "plan_tier": user.plan_tier,
        "plan_name": plan["name"],
        "monthly_token_quota": user.monthly_token_quota,
        "monthly_tokens_used": user.monthly_tokens_used,
        "monthly_tokens_remaining": max(0, user.monthly_token_quota - user.monthly_tokens_used),
        "usage_percentage": min(100.0, usage_percent),
        "all_time_tokens": all_time_tokens,
        "all_time_cost_usd": round(all_time_cost, 4)
    }

@router.get("/invoices")
def list_invoices(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoices = db.query(SubscriptionInvoice).filter(SubscriptionInvoice.user_id == user.id).order_by(SubscriptionInvoice.created_at.desc()).all()
    return [
        {
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "plan_tier": inv.plan_tier,
            "amount": inv.amount,
            "currency": inv.currency,
            "status": inv.status,
            "payment_method": inv.payment_method,
            "created_at": inv.created_at.isoformat()
        } for inv in invoices
    ]

@router.post("/subscribe")
def subscribe_plan(
    req: SubscribeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if req.plan_tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {list(SUBSCRIPTION_PLANS.keys())}"
        )

    selected_plan = SUBSCRIPTION_PLANS[req.plan_tier]

    # Update user plan and quota
    user.plan_tier = req.plan_tier
    user.monthly_token_quota = selected_plan["tokens_included"]

    # Generate billing invoice
    inv_num = f"INV-2026-{secrets.token_hex(3).upper()}"
    invoice = SubscriptionInvoice(
        user_id=user.id,
        invoice_number=inv_num,
        plan_tier=req.plan_tier,
        amount=selected_plan["price_monthly"],
        currency="USD",
        status="paid",
        payment_method=req.payment_method or "Visa ending in 4242",
        created_at=datetime.utcnow()
    )
    db.add(invoice)
    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": f"Successfully updated subscription to {selected_plan['name']}.",
        "invoice_number": inv_num,
        "plan": selected_plan
    }
