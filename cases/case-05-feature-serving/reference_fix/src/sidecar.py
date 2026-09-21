"""Feature enrichment sidecar — reference fix (async, cached, pooled, fails safe)."""
import logging
import os
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException

logger = logging.getLogger("feature-sidecar")

FEATURE_SERVICE = os.environ.get("FEATURE_SERVICE", "http://feature-service.internal:8080")
CACHE_TTL_S = 60          # hot accounts: 80% of traffic -> cache for repeat lookups
STALE_LIMIT_S = 300       # incident policy: last-known features usable <= 5 min
TIMEOUT = httpx.Timeout(connect=1.0, read=2.0, write=1.0, pool=1.0)

client: httpx.AsyncClient | None = None
_cache: dict[str, tuple[float, dict]] = {}  # account_id -> (fetched_at, features)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = httpx.AsyncClient(
        base_url=FEATURE_SERVICE, timeout=TIMEOUT,
        limits=httpx.Limits(max_connections=200, max_keepalive_connections=50),
    )
    yield
    await client.aclose()


app = FastAPI(lifespan=lifespan)


async def fetch_features(account_id: str) -> dict:
    url = f"/accounts/{account_id}/features"
    last_exc = None
    for attempt in range(3):  # small retry with backoff on transient failures
        try:
            resp = await client.get(url)
            if resp.status_code >= 500:
                raise httpx.HTTPStatusError("5xx", request=resp.request, response=resp)
            resp.raise_for_status()
            data = resp.json()
            break
        except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
            last_exc = e
            if attempt == 2:
                raise
    # schema is validated explicitly — no silent defaults
    if "risk_score" not in data or "price_index" not in data:
        raise ValueError(f"feature payload missing keys: {data!r}")
    return {"account_risk_score": data["risk_score"],
            "region_price_index": data["price_index"]}


@app.post("/enrich")
async def enrich(payload: dict):
    account_id = payload["account_id"]
    now = time.monotonic()

    cached = _cache.get(account_id)
    if cached and now - cached[0] < CACHE_TTL_S:  # fresh cache hit
        return {"account_id": account_id, "source": "cache", **cached[1]}

    try:
        features = await fetch_features(account_id)
        _cache[account_id] = (now, features)
        return {"account_id": account_id, "source": "live", **features}
    except Exception:
        # degraded mode per incident policy: last-known features <= 5 min old,
        # loudly marked; otherwise fail fast
        if cached and now - cached[0] < STALE_LIMIT_S:
            logger.warning("serving stale features", extra={"account_id": account_id,
                                                            "age_s": now - cached[0]})
            return {"account_id": account_id, "source": "stale", **cached[1]}
        raise HTTPException(status_code=503, detail="feature service unavailable")
