"""
Manual API smoke tests — run against a live backend.

Usage:
    python test_api.py [base_url]

Default base_url: http://localhost:8000
"""

import os
import sys
from typing import Any, Callable

import httpx
from dotenv import load_dotenv

load_dotenv()

_PASS = 0
_FAIL = 0
_SKIP = 0


def _run(
    label: str,
    response: httpx.Response,
    *,
    expect_status: int = 200,
    summary: Callable[[Any], str] | None = None,
) -> bool:
    global _PASS, _FAIL

    status_ok = response.status_code == expect_status

    try:
        body = response.json()
    except Exception:
        body = response.text

    try:
        detail = summary(body) if (summary and status_ok) else repr(body)[:120]
    except Exception as exc:
        detail = f"(summary error: {exc})"

    tag = "PASS" if status_ok else "FAIL"
    print(f"[{tag}]  {label:<56}  HTTP {response.status_code}  |  {detail}")

    if status_ok:
        _PASS += 1
    else:
        _FAIL += 1

    return status_ok


def _skip(label: str, reason: str) -> None:
    global _SKIP
    _SKIP += 1
    print(f"[SKIP]  {label:<56}  {reason}")


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    has_api_key = bool(os.environ.get("GOOGLE_API_KEY"))

    print(f"\nTarget: {base_url}")
    if not has_api_key:
        print("WARNING: GOOGLE_API_KEY not set — all chat tests will be skipped.")
    print()

    client = httpx.Client(base_url=base_url, timeout=10.0)

    with client:
        # ------------------------------------------------------------------
        # GET /health
        # ------------------------------------------------------------------
        r = client.get("/health")
        _run(
            "GET /health",
            r,
            summary=lambda b: (
                f"status={b.get('status')}  "
                f"time={b.get('time', '')[:19]}  "
                f"db={b.get('db', {})}"
            ),
        )

        # ------------------------------------------------------------------
        # GET /orders
        # ------------------------------------------------------------------
        r = client.get("/orders")
        _run(
            "GET /orders",
            r,
            summary=lambda b: (
                f"count={len(b)}  "
                f"first_status={b[0].get('status') if b else 'n/a'}"
            ),
        )

        # ------------------------------------------------------------------
        # GET /orders?status=pending
        # ------------------------------------------------------------------
        r = client.get("/orders", params={"status": "pending"})
        _run(
            "GET /orders?status=pending",
            r,
            summary=lambda b: (
                f"count={len(b)}  "
                f"all_pending={all(o['status'] == 'pending' for o in b)}"
            ),
        )

        # ------------------------------------------------------------------
        # GET /orders?status=invalid  (expect 422)
        # ------------------------------------------------------------------
        r = client.get("/orders", params={"status": "flying"})
        _run(
            "GET /orders?status=flying  (expect 422)",
            r,
            expect_status=422,
            summary=lambda b: f"detail present={bool(b.get('detail'))}",
        )

        # ------------------------------------------------------------------
        # GET /orders/{id}
        # ------------------------------------------------------------------
        r = client.get("/orders/1")
        _run(
            "GET /orders/1",
            r,
            summary=lambda b: (
                f"id={b.get('id')}  "
                f"status={b.get('status')}  "
                f"customer_id={b.get('customer_id')}"
            ),
        )

        # ------------------------------------------------------------------
        # GET /orders/{id} — not found
        # ------------------------------------------------------------------
        r = client.get("/orders/999999")
        _run(
            "GET /orders/999999  (expect 404)",
            r,
            expect_status=404,
            summary=lambda b: f"detail={b.get('detail')}",
        )

        # ------------------------------------------------------------------
        # PATCH /orders/{id}/status  (idempotent: read → change → restore)
        # ------------------------------------------------------------------
        r = client.get("/orders/1")
        if r.status_code == 200:
            original_status = r.json().get("status", "pending")
            target_status = "shipped" if original_status != "shipped" else "pending"

            r = client.patch("/orders/1/status", json={"status": target_status})
            _run(
                f"PATCH /orders/1/status → {target_status}",
                r,
                summary=lambda b: f"status={b.get('status')}",
            )

            r = client.patch("/orders/1/status", json={"status": original_status})
            _run(
                f"PATCH /orders/1/status → {original_status}  (restore)",
                r,
                summary=lambda b: f"status={b.get('status')}",
            )
        else:
            _skip("PATCH /orders/1/status", "order #1 not found, cannot run PATCH test")

        # ------------------------------------------------------------------
        # PATCH /orders/{id}/status — invalid value  (expect 422)
        # ------------------------------------------------------------------
        r = client.patch("/orders/1/status", json={"status": "teleporting"})
        _run(
            "PATCH /orders/1/status  invalid  (expect 422)",
            r,
            expect_status=422,
            summary=lambda b: f"detail present={bool(b.get('detail'))}",
        )

        # ------------------------------------------------------------------
        # GET /stock
        # ------------------------------------------------------------------
        r = client.get("/stock")
        _run(
            "GET /stock",
            r,
            summary=lambda b: (
                f"count={len(b)}  "
                + (
                    f"first={b[0].get('name')}  amt={b[0].get('stock_amount')}"
                    if b else "empty"
                )
            ),
        )

        # ------------------------------------------------------------------
        # GET /stock/critical
        # ------------------------------------------------------------------
        r = client.get("/stock/critical")
        _run(
            "GET /stock/critical",
            r,
            summary=lambda b: (
                f"count={len(b)}  "
                + (
                    f"first={b[0].get('name')} "
                    f"({b[0].get('stock_amount')}/{b[0].get('critical_threshold')})"
                    if b else "none critical"
                )
            ),
        )

        # ------------------------------------------------------------------
        # PATCH /stock/{id}  (idempotent: read → change → restore)
        # ------------------------------------------------------------------
        r = client.get("/stock")
        if r.status_code == 200 and r.json():
            product = r.json()[0]
            product_id = product["id"]
            original_amount = product["stock_amount"]
            target_amount = original_amount + 1000

            r = client.patch(f"/stock/{product_id}", json={"stock_amount": target_amount})
            _run(
                f"PATCH /stock/{product_id}  stock_amount → {target_amount}",
                r,
                summary=lambda b: f"stock_amount={b.get('stock_amount')}",
            )

            r = client.patch(f"/stock/{product_id}", json={"stock_amount": original_amount})
            _run(
                f"PATCH /stock/{product_id}  stock_amount → {original_amount}  (restore)",
                r,
                summary=lambda b: f"stock_amount={b.get('stock_amount')}",
            )
        else:
            _skip("PATCH /stock/{id}", "no products found, cannot run PATCH test")

        # ------------------------------------------------------------------
        # PATCH /stock/{id} — negative amount  (expect 422)
        # ------------------------------------------------------------------
        r = client.patch("/stock/1", json={"stock_amount": -1})
        _run(
            "PATCH /stock/1  negative amount  (expect 422)",
            r,
            expect_status=422,
            summary=lambda b: f"detail present={bool(b.get('detail'))}",
        )

        # ------------------------------------------------------------------
        # GET /cargo/track/{tracking_id}
        # ------------------------------------------------------------------
        r = client.get("/cargo/track/TRK-001")
        _run(
            "GET /cargo/track/TRK-001",
            r,
            summary=lambda b: (
                f"carrier={b.get('carrier')}  "
                f"status={b.get('status')}  "
                f"eta={b.get('estimated_delivery')}"
            ),
        )

        # ------------------------------------------------------------------
        # GET /cargo/delays
        # ------------------------------------------------------------------
        r = client.get("/cargo/delays")
        _run(
            "GET /cargo/delays",
            r,
            summary=lambda b: (
                f"count={len(b)}  "
                + (
                    f"first_order={b[0].get('order_id')} status={b[0].get('status')}"
                    if b else "none delayed"
                )
            ),
        )

        # ------------------------------------------------------------------
        # POST /api/chat  channel=web
        # ------------------------------------------------------------------
        if not has_api_key:
            _skip("POST /api/chat  channel=web", "GOOGLE_API_KEY not set")
        else:
            r = client.post(
                "/api/chat",
                json={"message": "Merhaba, siparişim nerede?", "customer_id": 1, "channel": "web"},
                timeout=60.0,
            )
            _run(
                "POST /api/chat  channel=web",
                r,
                summary=lambda b: (
                    f"response={b.get('response', '')[:60]!r}  "
                    f"channel={b.get('channel')}"
                ),
            )

        # ------------------------------------------------------------------
        # POST /api/chat  channel=whatsapp
        # ------------------------------------------------------------------
        if not has_api_key:
            _skip("POST /api/chat  channel=whatsapp", "GOOGLE_API_KEY not set")
        else:
            r = client.post(
                "/api/chat",
                json={"message": "Stok durumu nedir?", "customer_id": 2, "channel": "whatsapp"},
                timeout=60.0,
            )
            _run(
                "POST /api/chat  channel=whatsapp",
                r,
                summary=lambda b: (
                    f"response={b.get('response', '')[:60]!r}  "
                    f"channel={b.get('channel')}"
                ),
            )

        # ------------------------------------------------------------------
        # POST /api/chat/admin
        # ------------------------------------------------------------------
        if not has_api_key:
            _skip("POST /api/chat/admin", "GOOGLE_API_KEY not set")
        else:
            r = client.post(
                "/api/chat/admin",
                json={
                    "message": "Bugünkü stok ve sipariş durumu nasıl?",
                    "admin_id": 1,
                    "channel": "dashboard",
                },
                timeout=60.0,
            )
            _run(
                "POST /api/chat/admin",
                r,
                summary=lambda b: (
                    f"response={b.get('response', '')[:60]!r}  "
                    f"channel={b.get('channel')}"
                ),
            )

    # ----------------------------------------------------------------------
    total = _PASS + _FAIL
    skip_note = f"  ({_SKIP} skipped)" if _SKIP else ""
    outcome = "✓" if _FAIL == 0 else f"  ({_FAIL} failed)"
    print(f"\n{'─' * 70}")
    print(f"Result: {_PASS}/{total} passed{skip_note}{outcome}")
    print()

    sys.exit(0 if _FAIL == 0 else 1)


if __name__ == "__main__":
    main()
