"""
bot.py — KoopPilot Telegram Bot Ana Başlatıcı.

Kullanım:
    python bot.py                  # İki botu birden başlatır (admin + müşteri)
    python bot.py --mode admin     # Sadece admin bot
    python bot.py --mode customer  # Sadece müşteri bot

Environment Variables:
    TELEGRAM_ADMIN_BOT_TOKEN       — Admin bot token'ı
    TELEGRAM_CUSTOMER_BOT_TOKEN    — Müşteri bot token'ı
    TELEGRAM_ADMIN_USER_IDS        — Virgülle ayrılmış admin user ID'leri
    BACKEND_URL                    — Backend API URL (varsayılan: http://backend:8000)
"""

import argparse
import asyncio
import logging
import sys

from config import ADMIN_BOT_TOKEN, CUSTOMER_BOT_TOKEN

logger = logging.getLogger(__name__)


def main():
    """CLI argümanlarını parse edip ilgili botu başlatır."""
    parser = argparse.ArgumentParser(description="KoopPilot Telegram Bot")
    parser.add_argument(
        "--mode",
        choices=["admin", "customer", "both"],
        default="both",
        help="Hangi bot(lar) başlatılacak (varsayılan: both)",
    )
    args = parser.parse_args()

    # Logging yapılandırması
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if args.mode == "admin":
        _run_admin()
    elif args.mode == "customer":
        _run_customer()
    else:
        _run_both()


def _run_admin():
    """Sadece admin bot'u başlatır."""
    if not ADMIN_BOT_TOKEN:
        logger.error("TELEGRAM_ADMIN_BOT_TOKEN ayarlanmamış. .env dosyasını kontrol edin.")
        sys.exit(1)

    from admin_bot import run_admin_bot

    logger.info("🟢 Admin bot başlatılıyor...")
    run_admin_bot()


def _run_customer():
    """Sadece müşteri bot'u başlatır."""
    if not CUSTOMER_BOT_TOKEN:
        logger.error("TELEGRAM_CUSTOMER_BOT_TOKEN ayarlanmamış. .env dosyasını kontrol edin.")
        sys.exit(1)

    from customer_bot import run_customer_bot

    logger.info("🟢 Müşteri bot başlatılıyor...")
    run_customer_bot()


def _run_both():
    """İki botu aynı anda başlatır (asyncio ile)."""
    if not ADMIN_BOT_TOKEN and not CUSTOMER_BOT_TOKEN:
        logger.error(
            "Hiçbir bot token'ı ayarlanmamış.\n"
            "TELEGRAM_ADMIN_BOT_TOKEN ve/veya TELEGRAM_CUSTOMER_BOT_TOKEN .env'ye ekleyin."
        )
        sys.exit(1)

    # Her bot kendi polling loop'unu çalıştırdığından, iki botu aynı process'te
    # çalıştırmak karmaşık. En temiz yaklaşım: ayrı process'lerde.
    import multiprocessing

    processes = []

    if ADMIN_BOT_TOKEN:
        p = multiprocessing.Process(target=_run_admin, name="admin-bot")
        processes.append(p)
        logger.info("Admin bot process'i oluşturuldu.")
    else:
        logger.warning("TELEGRAM_ADMIN_BOT_TOKEN yok — admin bot atlanıyor.")

    if CUSTOMER_BOT_TOKEN:
        p = multiprocessing.Process(target=_run_customer, name="customer-bot")
        processes.append(p)
        logger.info("Müşteri bot process'i oluşturuldu.")
    else:
        logger.warning("TELEGRAM_CUSTOMER_BOT_TOKEN yok — müşteri bot atlanıyor.")

    # Process'leri başlat
    for p in processes:
        p.start()
        logger.info("🟢 %s başlatıldı (PID: %d)", p.name, p.pid)

    # Ctrl+C ile temiz çıkış
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        logger.info("Kapatma sinyali alındı...")
        for p in processes:
            p.terminate()
            p.join(timeout=5)
        logger.info("Tüm bot'lar kapatıldı.")


if __name__ == "__main__":
    main()
