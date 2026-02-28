"""
Authentication utilities: password hashing, JWT token generation and verification
"""
import hashlib
import hmac
import json
import base64
import time
import os
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get("SECRET_KEY", "smartgov_secret_key_2024_change_in_prod")
TOKEN_EXPIRY_HOURS = 24


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against its hash"""
    return hash_password(plain_password) == hashed_password


def create_token(user_id: int, email: str, role: str) -> str:
    """Create a simple signed JWT-like token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": time.time() + (TOKEN_EXPIRY_HOURS * 3600),
        "iat": time.time()
    }
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"


def verify_token(token: str) -> dict | None:
    """Verify and decode token, returns payload or None"""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, signature = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload = json.loads(base64.b64decode(payload_b64).decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def generate_complaint_number() -> str:
    """Generate unique complaint number like COMP-2024-00001"""
    year = datetime.now().year
    timestamp = int(time.time() * 1000) % 100000
    return f"COMP-{year}-{timestamp:05d}"
