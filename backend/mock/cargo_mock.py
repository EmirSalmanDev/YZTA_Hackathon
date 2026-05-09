import hashlib
from datetime import date, timedelta

_CARRIERS = [
    "Yurtiçi Kargo",
    "Aras Kargo",
    "MNG Kargo",
    "PTT Kargo",
    "Sürat Kargo",
]

_CITIES = [
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya",
    "Adana", "Konya", "Gaziantep", "Kayseri", "Eskişehir",
]

_ACTIVE_STATUSES = [
    "Kargoya Verildi",
    "Transfer Merkezinde",
    "Dağıtımda",
    "Teslim Edildi",
]

_DELAYED_STATUS = "Gecikmiş"


def _sha_int(tracking_id: str, salt: str = "") -> int:
    # hashlib instead of hash() — stable across processes regardless of PYTHONHASHSEED
    payload = f"{tracking_id}{salt}".encode()
    return int(hashlib.sha256(payload).hexdigest(), 16)


def track_shipment(tracking_id: str) -> dict:
    """Return a deterministic mock shipment record for *tracking_id*.

    The same ID always produces the same carrier, status, and location.
    20 % of IDs resolve to a delayed status (hash % 10 < 2).
    estimated_delivery is a hash-derived number of days from today, so the
    offset is stable even though the absolute date advances with the calendar.
    """
    is_delayed = _sha_int(tracking_id) % 10 < 2
    status = (
        _DELAYED_STATUS
        if is_delayed
        else _ACTIVE_STATUSES[_sha_int(tracking_id, "status") % len(_ACTIVE_STATUSES)]
    )
    carrier = _CARRIERS[_sha_int(tracking_id, "carrier") % len(_CARRIERS)]
    location = _CITIES[_sha_int(tracking_id, "loc") % len(_CITIES)]
    days_ahead = 1 + _sha_int(tracking_id, "eta") % 7
    estimated_delivery = (date.today() + timedelta(days=days_ahead)).isoformat()

    return {
        "tracking_id": tracking_id,
        "carrier": carrier,
        "status": status,
        "location": location,
        "estimated_delivery": estimated_delivery,
    }


# Backward-compat shim — api/cargo.py and agent/tools/cargo_tools.py import this name
def get_mock_status(tracking_id: str) -> dict:
    return track_shipment(tracking_id)


if __name__ == "__main__":
    # Smoke: same ID → same result; 20% delayed distribution holds
    samples = [f"TRK-{i:04d}" for i in range(100)]
    delayed = [s for s in samples if track_shipment(s)["status"] == _DELAYED_STATUS]
    assert track_shipment("TRK-0001") == track_shipment("TRK-0001"), "not deterministic"
    assert 10 <= len(delayed) <= 30, f"delayed rate out of range: {len(delayed)}/100"
    print(f"smoke ok — {len(delayed)}/100 delayed")
