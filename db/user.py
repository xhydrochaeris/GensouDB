import secrets
from argon2 import PasswordHasher
from datetime import datetime, timezone, timedelta
from db.db import get_conn, pack, unpack

ph = PasswordHasher()

def get_uid(username):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT ID FROM USER WHERE uname = ?", (username,)
        ).fetchone()
        if not row:
            return -1 # User doesn't exist
        else:
            return dict(row)['ID']

def dname_collision(dname):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM USER WHERE dname = ?", (dname,)
        ).fetchone()
        if not row:
            return False
        else:
            return True

def hash_password(plaintext: str) -> str:
    return ph.hash(plaintext)

def store_hash_password(uid, pt):
    phash = hash_password(pt)
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "UPDATE USER SET pw_hash = ?, pw_date = ?, dummy_pw = ? WHERE ID = ?", (phash, now, False, uid,)
        )

def create_user(dname, uname, pwd):
    phash = hash_password(pwd)
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO USER (dname, uname, pw_hash, pw_date, dummy_pw) values (?, ?, ?, ?, ?)", (dname, uname, phash, now, False)
        )
        return cursor.lastrowid

def verify_password(uid, plaintext):
    # Return 0 (false), 1 (true), 2 (dummy), 3 (uninit)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT pw_hash,dummy_pw FROM USER WHERE ID = ?", (uid,)
        ).fetchone()
        if not row:
            return 0 # User with that ID probably doesn't exist
        stored_hash = dict(row)['pw_hash']
        is_dummy = dict(row)['dummy_pw']
        if stored_hash is None:
            return 3 # No password for this user in database
        else:
            if is_dummy:
                try:
                    ph.verify(stored_hash, plaintext)
                    return 2 # Password matches dummy
                except Exception:
                    return 0 # Password does not match dummy
            else:
                try:
                    ph.verify(stored_hash, plaintext)
                    return 1 # Password matches
                except Exception:
                    return 0 # Password does not match

def get_uname(uid):
    with get_conn() as conn:
        r = conn.execute("SELECT uname FROM USER WHERE ID = ?", (user,)).fetchone()
        return r[0]

def get_dname(uid):
    with get_conn() as conn:
        r = conn.execute("SELECT dname FROM USER WHERE ID = ?", (user,)).fetchone()
        return r[0]

def pwd_is_dummy(uid):
    # Return 0 (false), 1 (true), 2 (error)
    with get_conn() as conn:
        row = conn.execute(
            "SELECT dummy_pw FROM USER WHERE ID = ?", (uid,)
        ).fetchone()
        if not row:
            return 2 # User with that ID probably doesn't exist
        is_dummy = dict(row)['dummy_pw']
        if is_dummy:
            return 1
        else:
            return 0
    
def is_session_valid(uid, sess_id: str) -> bool:
    with get_conn() as conn:
        if uid is None:
            return False
        row = conn.execute(
            "SELECT SESS_ID, SESS_Expiry FROM USER WHERE ID = ?", (uid,)
        ).fetchone()
        if not row:
            return False # User with that ID probably doesn't exist
        stored_sess_id = dict(row)['SESS_ID']
        expiry_str = dict(row)['SESS_Expiry']
        if sess_id != stored_sess_id:
            return False
        expiry = datetime.fromisoformat(expiry_str).replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < expiry

def new_session(uid, days=30) -> tuple[str, str]:
    sess_id     = secrets.token_hex(32)
    sess_expiry = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
    with get_conn() as conn:
        cursor = conn.execute("""
            UPDATE USER SET SESS_ID = ? WHERE ID = ?
        """, (
            sess_id,
            uid
        ))
        cursor = conn.execute("""
            UPDATE USER SET SESS_Expiry = ? WHERE ID = ?
        """, (
            sess_expiry,
            uid
        ))
    return sess_id, sess_expiry

def destroy_session(uid):
    with get_conn() as conn:
        sess_expiry = (datetime.now(timezone.utc)).isoformat()
        cursor = conn.execute("""
            UPDATE USER SET SESS_Expiry = ? WHERE ID = ?
        """, (
            sess_expiry,
            uid
        ))

def get_privilege(uid):
    with get_conn() as conn:
        if uid is None:
            return -1 # Not logged in
        row = conn.execute(
            "SELECT class FROM USER WHERE ID = ?", (uid,)
        ).fetchone()
        if not row:
            return -1 # User ID doesn't exist'
        return dict(row)['class']
