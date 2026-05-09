from typing import Optional

MOCK_CARGO: dict[str, dict] = {
    "TRK-001": {
        "tracking_id": "TRK-001",
        "carrier": "Yurtiçi Kargo",
        "status": "Dağıtımda",
        "last_update": "2026-05-09T08:30:00",
    },
    "TRK-002": {
        "tracking_id": "TRK-002",
        "carrier": "Aras Kargo",
        "status": "Transfer Merkezinde",
        "last_update": "2026-05-08T22:00:00",
    },
    "TRK-003": {
        "tracking_id": "TRK-003",
        "carrier": "MNG Kargo",
        "status": "Teslim Edildi",
        "last_update": "2026-05-07T14:15:00",
    },
}


def get_mock_status(tracking_id: str) -> Optional[dict]:
    return MOCK_CARGO.get(tracking_id)


if __name__ == "__main__":
    print("smoke ok")
