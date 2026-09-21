"""Feature enrichment sidecar."""
import requests
import numpy as np
from fastapi import FastAPI

app = FastAPI()
FEATURE_SERVICE = "http://feature-service.internal:8080"


def get_features(account_id: str) -> dict:
    url = f"{FEATURE_SERVICE}/accounts/{account_id}/features"
    resp = requests.get(url)
    data = resp.json()
    return {
        "account_risk_score": data.get("risk_score", 0.5),
        "region_price_index": data.get("price_index", 1.0),
    }


@app.post("/enrich")
async def enrich(payload: dict):
    features = get_features(payload["account_id"])
    return {"account_id": payload["account_id"], **features}
