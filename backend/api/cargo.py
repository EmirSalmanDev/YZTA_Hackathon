from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mock.cargo_mock import get_mock_status

router = APIRouter()


class CargoStatus(BaseModel):
    tracking_id: str
    carrier: str
    status: str
    last_update: str


@router.get("/cargo/track/{tracking_id}", response_model=CargoStatus)
async def track_cargo(tracking_id: str) -> CargoStatus:
    result = get_mock_status(tracking_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Tracking ID not found")
    return CargoStatus(**result)


if __name__ == "__main__":
    print("smoke ok")
