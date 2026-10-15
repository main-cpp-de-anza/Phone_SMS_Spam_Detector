"""Dedicated Vercel function for POST /api/predict."""

import sys
from pathlib import Path

from fastapi import FastAPI

website_dir = Path(__file__).resolve().parents[1]
if str(website_dir) not in sys.path:
    sys.path.insert(0, str(website_dir))

from app import PredictRequest, predict_endpoint  # noqa: E402

app = FastAPI(title="SMS Spam Prediction API")


@app.post("/")
def predict(req: PredictRequest):
    return predict_endpoint(req)

