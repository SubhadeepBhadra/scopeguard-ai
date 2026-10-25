import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

# In-memory session store mapped to user_id with expiration
# In production with Redis or database sessions, this provides instant revocable sessions
ACTIVE_SESSIONS = {}  # token -> {"user_id": int, "expires_at": datetime}

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a unique cryptographic salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}:{key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against the stored salt:hash string."""
    try:
        salt, stored_hash = hashed_password.split(':')
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return secrets.compare_digest(key.hex(), stored_hash)
    except Exception:
        return False

def create_session(user_id: int, days: int = 7) -> str:
    """Generate a high-entropy session token and register it with an expiration timestamp."""
    token = f"sg_{secrets.token_urlsafe(32)}"
    expires_at = datetime.utcnow() + timedelta(days=days)
    ACTIVE_SESSIONS[token] = {
        "user_id": user_id,
        "expires_at": expires_at
    }
    return token

def revoke_session(token: str):
    """Revoke an active session."""
    if token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Extract authenticated user from Bearer header or Cookie."""
    token = None
    if credentials:
        token = credentials.credentials
    else:
        # Check cookie
        token = request.cookies.get("sg_session")

    if not token or token not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session_data = ACTIVE_SESSIONS[token]
    if datetime.utcnow() > session_data["expires_at"]:
        del ACTIVE_SESSIONS[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please log in again.",
        )

    user = db.query(User).filter(User.id == session_data["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user
