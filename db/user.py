import secrets
from argon2 import PasswordHasher
from datetime import datetime, timezone, timedelta

ph = PasswordHasher()

def hash_password(plaintext: str) -> str:
    return ph.hash(plaintext)

def verify_password(stored_hash: str, plaintext: str) -> bool:
    try:
        ph.verify(stored_hash, plaintext)
        return True
    except Exception:
        return False
    
def is_session_valid(sess_id: str, stored_sess_id: str, expiry_str: str) -> bool:
    if sess_id != stored_sess_id:
        return False
    expiry = datetime.fromisoformat(expiry_str).replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < expiry

def new_session(days=30) -> tuple[str, str]:
    sess_id     = secrets.token_hex(32)
    sess_expiry = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    return sess_id, sess_expiry