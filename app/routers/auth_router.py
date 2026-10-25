from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..auth import hash_password, verify_password, create_session, revoke_session, get_current_user, ACTIVE_SESSIONS

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    company_name: Optional[str] = "Independent Studio"
    role: Optional[str] = "director"
    default_hourly_rate: Optional[float] = 125.0
    currency: Optional[str] = "USD"

class LoginRequest(BaseModel):
    email: str
    password: str

class DemoLoginRequest(BaseModel):
    role: str = "director"  # 'director' or 'freelancer'

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    default_hourly_rate: Optional[float] = None
    currency: Optional[str] = None
    custom_groq_key: Optional[str] = None
    custom_openai_key: Optional[str] = None

@router.post("/register")
def register(req: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user = User(
        email=req.email.lower(),
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        company_name=req.company_name,
        role=req.role,
        default_hourly_rate=req.default_hourly_rate,
        currency=req.currency,
        plan_tier="pro",
        monthly_token_quota=500000,
        monthly_tokens_used=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_session(user.id)
    response.set_cookie(key="sg_session", value=token, httponly=True, max_age=86400 * 7, samesite="lax")

    return {
        "status": "success",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "role": user.role,
            "plan_tier": user.plan_tier,
            "monthly_token_quota": user.monthly_token_quota,
            "monthly_tokens_used": user.monthly_tokens_used,
            "default_hourly_rate": user.default_hourly_rate,
            "currency": user.currency
        }
    }

@router.post("/login")
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password combination."
        )

    token = create_session(user.id)
    response.set_cookie(key="sg_session", value=token, httponly=True, max_age=86400 * 7, samesite="lax")

    return {
        "status": "success",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "role": user.role,
            "plan_tier": user.plan_tier,
            "monthly_token_quota": user.monthly_token_quota,
            "monthly_tokens_used": user.monthly_tokens_used,
            "default_hourly_rate": user.default_hourly_rate,
            "currency": user.currency
        }
    }

@router.post("/demo-login")
def demo_login(req: DemoLoginRequest, response: Response, db: Session = Depends(get_db)):
    """Instant login for demonstration and review purposes."""
    target_email = "director@scopeguard.ai" if req.role == "director" else "freelancer@scopeguard.ai"
    user = db.query(User).filter(User.email == target_email).first()

    if not user:
        # Fallback if seed not run yet
        user = User(
            email=target_email,
            hashed_password=hash_password("password123"),
            full_name="Elena Rostova" if req.role == "director" else "Marcus Chen",
            company_name="Apex Studio Labs" if req.role == "director" else "Chen Product Studio",
            role=req.role,
            plan_tier="pro" if req.role == "director" else "starter",
            monthly_token_quota=500000 if req.role == "director" else 100000,
            monthly_tokens_used=64850 if req.role == "director" else 12400,
            default_hourly_rate=150.0 if req.role == "director" else 95.0,
            currency="USD"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_session(user.id)
    response.set_cookie(key="sg_session", value=token, httponly=True, max_age=86400 * 7, samesite="lax")

    return {
        "status": "success",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "role": user.role,
            "plan_tier": user.plan_tier,
            "monthly_token_quota": user.monthly_token_quota,
            "monthly_tokens_used": user.monthly_tokens_used,
            "default_hourly_rate": user.default_hourly_rate,
            "currency": user.currency
        }
    }

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "company_name": user.company_name,
        "role": user.role,
        "plan_tier": user.plan_tier,
        "monthly_token_quota": user.monthly_token_quota,
        "monthly_tokens_used": user.monthly_tokens_used,
        "default_hourly_rate": user.default_hourly_rate,
        "currency": user.currency,
        "has_custom_groq": bool(user.custom_groq_key),
        "has_custom_openai": bool(user.custom_openai_key)
    }

@router.put("/profile")
def update_profile(
    req: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if req.full_name is not None:
        user.full_name = req.full_name
    if req.company_name is not None:
        user.company_name = req.company_name
    if req.default_hourly_rate is not None:
        user.default_hourly_rate = req.default_hourly_rate
    if req.currency is not None:
        user.currency = req.currency
    if req.custom_groq_key is not None:
        user.custom_groq_key = req.custom_groq_key
    if req.custom_openai_key is not None:
        user.custom_openai_key = req.custom_openai_key

    db.commit()
    db.refresh(user)

    return {"status": "success", "message": "Profile updated successfully."}

@router.post("/logout")
def logout(response: Response, user: User = Depends(get_current_user)):
    response.delete_cookie("sg_session")
    return {"status": "success", "message": "Logged out successfully."}
