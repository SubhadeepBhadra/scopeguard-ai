import hashlib
import secrets
from datetime import datetime, timedelta

# In-memory session store mapped to user_id with expiration
ACTIVE_SESSIONS = {}  # token -> {"user_id": int, "expires_at": datetime}

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
