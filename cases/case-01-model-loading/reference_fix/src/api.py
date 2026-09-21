"""Churn scoring service — reference fix."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from predictor import ChurnModel, FEATURES

logger = logging.getLogger("churn-service")
state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"] = ChurnModel()  # heavy load once, at startup; crash here if broken
    yield


app = FastAPI(lifespan=lifespan)


class ChurnRequest(BaseModel):
    tenure_months: float
    monthly_spend: float
    num_support_tickets: int
    days_since_last_login: float
    plan_type: int
    has_auto_pay: bool
    num_logins_30d: int
    avg_session_minutes: float
    num_devices: int
    discount_pct: float
    contract_length: int
    late_payments: int
    data_usage_gb: float
    voicemail_enabled: bool


@app.get("/healthz")
def healthz():
    return {"status": "ok", "model_version": state["model"].version}


@app.post("/predict")
def predict(req: ChurnRequest):
    score = state["model"].predict_proba([req.model_dump()])[0]
    logger.info("prediction", extra={"model_version": state["model"].version})
    return {"churn_probability": float(score), "model_version": state["model"].version}


@app.post("/predict_batch")
def predict_batch(reqs: list[ChurnRequest]):
    scores = state["model"].predict_proba([r.model_dump() for r in reqs])  # one vectorized call
    return {"scores": scores.tolist(), "model_version": state["model"].version}
