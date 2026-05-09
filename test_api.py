"""
Manual API smoke tests — run against a live backend.

Usage:
    python test_api.py [base_url]

Default base_url: http://localhost:8000
"""

import sys
from typing import Any, Callable

import httpx

_PASS = 0
_FAIL = 0


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
        detail = summary(body) if (summary and status_ok) else repr(body)[:100]
    except Exception as exc:
        detail = f"(summary error: {exc})"

    tag = "PASS" if status_ok else "FAIL"
    print(f"[{tag}]  {label:<46}  HTTP {response.status_code}  |  {detail}")

    if status_ok:
        _PASS += 1
    else:
        _FAIL += 1

    return status_ok


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print(f"\nTarget: {base_url}\n")

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
            summary=lambda b: f"count={len(b)}  first_status={b[0].get('status') if b else 'n/a'}",
        )

        # ------------------------------------------------------------------
        # GET /orders?status=pending
        # ------------------------------------------------------------------
        r = client.get("/orders", params={"status": "pending"})
        _run(
            "GET /orders?status=pending",
            r,
            summary=lambda b: f"count={len(b)}  all_pending={all(o['status']=='pending' for o in b)}",
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
        # GET /stock/critical
        # ------------------------------------------------------------------
        r = client.get("/stock/critical")
        _run(
            "GET /stock/critical",
            r,
            summary=lambda b: (
                f"count={len(b)}  "
                + (f"first={b[0].get('name')} ({b[0].get('stock_amount')}/{b[0].get('critical_threshold')})" if b else "none")
            ),
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
        # POST /chat  channel=web
        # ------------------------------------------------------------------
        r = client.post(
            "/chat",
            json={"message": "Merhaba, siparişim nerede?", "customer_id": 1, "channel": "web"},
        )
        _run(
            "POST /chat  channel=web",
            r,
            summary=lambda b: (
                f"reply={b.get('reply')!r}  "
                f"agent_used_tool={b.get('agent_used_tool')!r}"
            ),
        )

        # ------------------------------------------------------------------
        # POST /chat  channel=whatsapp
        # ------------------------------------------------------------------
        r = client.post(
            "/chat",
            json={"message": "Stok durumu nedir?", "customer_id": 2, "channel": "whatsapp"},
        )
        _run(
            "POST /chat  channel=whatsapp",
            r,
            summary=lambda b: (
                f"reply={b.get('reply')!r}  "
                f"agent_used_tool={b.get('agent_used_tool')!r}"
            ),
        )

        # ------------------------------------------------------------------
        # POST /chat  invalid channel (expect 422)
        # ------------------------------------------------------------------
        r = client.post(
            "/chat",
            json={"message": "test", "customer_id": 1, "channel": "sms"},
        )
        _run(
            "POST /chat  channel=sms  (expect 422)",
            r,
            expect_status=422,
            summary=lambda b: f"detail present={bool(b.get('detail'))}",
        )

    # ----------------------------------------------------------------------
    total = _PASS + _FAIL
    print(f"\n{'─' * 70}")
    print(f"Result: {_PASS}/{total} passed", "✓" if _FAIL == 0 else f"  ({_FAIL} failed)")
    print()

    sys.exit(0 if _FAIL == 0 else 1)


if __name__ == "__main__":
    main()
