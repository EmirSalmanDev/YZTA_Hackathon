"""
config.py — KoopPilot Telegram Bot Yapılandırması.

Environment variable'lardan token ve URL okuma.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# .env dosyasını yükle — Docker dışında çalışırken gerekli
# Önce proje kökündeki .env'yi, sonra yerel .env'yi dene
_project_root_env = Path(__file__).resolve().parent.parent / ".env"
if _project_root_env.exists():
    load_dotenv(_project_root_env)
else:
    load_dotenv()  # CWD'deki .env

# ---------------------------------------------------------------------------
# Backend API URL
# ---------------------------------------------------------------------------
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

# ---------------------------------------------------------------------------
# Telegram Bot Token'ları
# ---------------------------------------------------------------------------
ADMIN_BOT_TOKEN = os.environ.get("TELEGRAM_ADMIN_BOT_TOKEN", "")
CUSTOMER_BOT_TOKEN = os.environ.get("TELEGRAM_CUSTOMER_BOT_TOKEN", "")

# ---------------------------------------------------------------------------
# Kayıtlı Admin Kullanıcıları (Telegram User ID'leri)
# ---------------------------------------------------------------------------
# Güvenlik: Sadece bu listedeki kullanıcılar admin bot fonksiyonlarını kullanabilir.
# Virgülle ayrılmış ID listesi: "12345,67890"
_admin_ids_raw = os.environ.get("TELEGRAM_ADMIN_USER_IDS", "")
ADMIN_USER_IDS: set[int] = set()
if _admin_ids_raw:
    for uid in _admin_ids_raw.split(","):
        uid = uid.strip()
        if uid.isdigit():
            ADMIN_USER_IDS.add(int(uid))

# ---------------------------------------------------------------------------
# API Maliyet Azaltma
# ---------------------------------------------------------------------------
# Maksimum mesaj uzunluğu (token tasarrufu)
MAX_MESSAGE_LENGTH = 2000

# Konuşma geçmişi penceresi (bellekte tutulan mesaj sayısı)
CONVERSATION_WINDOW = 20

# Rate limiting (saniye cinsinden minimum mesaj aralığı)
MIN_MESSAGE_INTERVAL = 2
