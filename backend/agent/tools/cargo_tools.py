from typing import Optional

from mock.cargo_mock import get_mock_status


def track_cargo(tracking_id: str) -> Optional[dict]:
    return get_mock_status(tracking_id)


if __name__ == "__main__":
    print("smoke ok")
