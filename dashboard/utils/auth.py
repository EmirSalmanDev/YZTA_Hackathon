"""
auth.py — KoopPilot Dashboard Kimlik Doğrulama Modülü.

Demo amaçlı local SQLite veritabanı kullanır.
"""

import hashlib
import os
import secrets
import sqlite3
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Veritabanı yolu
# ---------------------------------------------------------------------------
_DB_DIR = Path("data")
_DB_DIR.mkdir(exist_ok=True)
_AUTH_DB = _DB_DIR / "dashboard_users.db"


def _get_conn() -> sqlite3.Connection:
    """SQLite bağlantısı döndürür, tablo yoksa oluşturur."""
    conn = sqlite3.connect(str(_AUTH_DB))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            phone TEXT DEFAULT '',
            telegram_bot_token TEXT DEFAULT '',
            telegram_customer_bot_token TEXT DEFAULT '',
            instagram_url TEXT DEFAULT '',
            whatsapp_url TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def _hash_password(password: str, salt: str) -> str:
    """SHA-256 + salt ile şifre hash'ler."""
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def require_auth() -> bool:
    """Kullanıcının oturum açıp açmadığını kontrol eder."""
    return st.session_state.get("authenticated", False)


def register_user(business_name: str, email: str, password: str) -> dict:
    """Yeni kullanıcı kaydeder."""
    email = email.strip().lower()
    if not business_name or not email or not password:
        return {"success": False, "error": "Tüm alanları doldurunuz."}
    
    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    now = datetime.utcnow().isoformat()

    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO users (business_name, email, password_hash, salt, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (business_name.strip(), email, password_hash, salt, now, now),
        )
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return {"success": True, "user": {"id": user["id"], "business_name": user["business_name"], "email": user["email"]}}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "Bu e-posta adresi zaten kayıtlı."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def login_user(email: str, password: str) -> dict:
    """Kullanıcı giriş doğrulaması."""
    email = email.strip().lower()
    try:
        conn = _get_conn()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not user: return {"success": False, "error": "E-posta veya şifre hatalı."}
        if _hash_password(password, user["salt"]) != user["password_hash"]:
            return {"success": False, "error": "E-posta veya şifre hatalı."}

        return {
            "success": True,
            "user": {
                "id": user["id"],
                "business_name": user["business_name"],
                "email": user["email"],
                "phone": user["phone"],
                "telegram_bot_token": user["telegram_bot_token"],
                "telegram_customer_bot_token": user["telegram_customer_bot_token"]
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def request_password_reset(email: str) -> dict:
    """Şifre sıfırlama talebi."""
    email = email.strip().lower()
    try:
        conn = _get_conn()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user:
            return {"success": True, "message": "E-posta kayıtlıysa sıfırlama bağlantısı gönderildi."}
        
        token = secrets.token_urlsafe(32)
        expires = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        conn.execute("INSERT INTO reset_tokens (email, token, expires_at) VALUES (?, ?, ?)", (email, token, expires))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Sıfırlama bağlantısı oluşturuldu.", "token": token}
    except Exception as e:
        return {"success": False, "error": str(e)}


def reset_password(token: str, new_password: str) -> dict:
    """Şifre sıfırlama."""
    try:
        conn = _get_conn()
        row = conn.execute("SELECT * FROM reset_tokens WHERE token = ? AND used = 0", (token,)).fetchone()
        if not row: return {"success": False, "error": "Geçersiz token."}
        
        salt = secrets.token_hex(16)
        pw_hash = _hash_password(new_password, salt)
        conn.execute("UPDATE users SET password_hash = ?, salt = ? WHERE email = ?", (pw_hash, salt, row["email"]))
        conn.execute("UPDATE reset_tokens SET used = 1 WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Şifre güncellendi."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_user_settings(user_id: int, **kwargs) -> dict:
    """Kullanıcı ayarlarını günceller."""
    allowed = {"business_name", "phone", "telegram_bot_token", "telegram_customer_bot_token"}
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    try:
        conn = _get_conn()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [datetime.utcnow().isoformat(), user_id]
        conn.execute(f"UPDATE users SET {set_clause}, updated_at = ? WHERE id = ?", values)
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return {"success": True, "user": dict(user)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def change_password(email: str, old_password: str, new_password: str) -> dict:
    """Şifre değiştirme."""
    try:
        conn = _get_conn()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user or _hash_password(old_password, user["salt"]) != user["password_hash"]:
            return {"success": False, "error": "Mevcut şifre hatalı."}
        
        salt = secrets.token_hex(16)
        password_hash = _hash_password(new_password, salt)
        conn.execute("UPDATE users SET password_hash = ?, salt = ? WHERE email = ?", (password_hash, salt, email))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def ensure_demo_user() -> None:
    """Demo kullanıcı oluşturur."""
    conn = _get_conn()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@kooppilot.com",)).fetchone()
    conn.close()
    if not existing:
        register_user("KoopPilot Demo", "demo@kooppilot.com", "demo123")
