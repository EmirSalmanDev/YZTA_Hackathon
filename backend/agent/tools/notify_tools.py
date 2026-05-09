import json
from pathlib import Path

ALERTS_FILE = Path("data/alerts.json")


def send_alert(message: str, level: str = "warning") -> dict:
    # TODO: integrate with Twilio or push notification system
    alert = {"message": message, "level": level}
    alerts = json.loads(ALERTS_FILE.read_text()) if ALERTS_FILE.exists() else []
    alerts.append(alert)
    ALERTS_FILE.write_text(json.dumps(alerts, ensure_ascii=False, indent=2))
    return alert


if __name__ == "__main__":
    print("smoke ok")
