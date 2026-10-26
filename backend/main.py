import json
import logging
import os
import sqlite3
import time
from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.schema import CustomerInput, PredictionOutput, risk_level

ROOT = Path(__file__).resolve().parents[1]
LOGGER = logging.getLogger("churnx")


class ModelService:
    def __init__(self, model_path, database):
        self.pipeline = joblib.load(model_path)
        self.metadata = json.loads(model_path.with_name("metadata.json").read_text(encoding="utf-8"))
        self.dashboard = json.loads(model_path.with_name("dashboard.json").read_text(encoding="utf-8"))
        self.database = database
        database.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(database)) as connection, connection:
            connection.execute("CREATE TABLE IF NOT EXISTS predictions (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, probability REAL NOT NULL, risk TEXT NOT NULL, prediction INTEGER NOT NULL, model_version TEXT NOT NULL)")
        self.monitor = {"requests": 0, "errors": 0, "total_latency_ms": 0.0, "predictions": 0, "probability_sum": 0.0, "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0}}
        self.lock = Lock()

    def predict(self, customer):
        row = customer.raw_row()
        frame = pd.DataFrame([row], columns=self.metadata["features"])
        probability = float(self.pipeline.predict_proba(frame)[0, 1])
        # Replace one field at a time with the training reference to measure model sensitivity.
        reference = self.metadata["reference_profile"]
        variants = [dict(row, **{column: reference[column]}) for column in frame.columns]
        alternatives = self.pipeline.predict_proba(pd.DataFrame(variants, columns=frame.columns))[:, 1]
        deltas = sorted(zip(frame.columns, alternatives), key=lambda item: probability - item[1], reverse=True)
        factors = [f"{column}: {row[column]} (+{(probability - alternative) * 100:.1f} pp versus training reference)" for column, alternative in deltas if probability - alternative > .002][:4]
        bands = self.metadata["risk_bands"]
        risk = risk_level(probability, bands["low"], bands["high"])
        prediction = int(probability >= self.metadata["threshold"])
        prediction_id = str(uuid4())
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute("INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?)", (prediction_id, datetime.now(timezone.utc).isoformat(), probability, risk, prediction, self.metadata["version"]))
        with self.lock:
            self.monitor["predictions"] += 1
            self.monitor["probability_sum"] += probability
            self.monitor["risk_distribution"][risk] += 1
        return PredictionOutput(prediction=prediction, churn_probability=probability, churn_percentage=round(probability * 100, 2), risk_level=risk,
                                model_version=self.metadata["version"], top_factors=factors,
                                explanation_method="Single-feature replacement sensitivity against training median/mode; association only, not causal or SHAP attribution.", prediction_id=prediction_id)


def create_app(model_path=None, database=None):
    path = Path(model_path or os.getenv("MODEL_PATH", ROOT / "models/churnx_pipeline.joblib"))
    db = Path(database or os.getenv("DATABASE_PATH", ROOT / "runtime/predictions.db"))

    @asynccontextmanager
    async def lifespan(app):
        app.state.service = None
        app.state.load_error = None
        try:
            app.state.service = ModelService(path, db)
        except Exception:
            LOGGER.exception("Model startup failed")
            app.state.load_error = "Model artifacts unavailable. Run the training pipeline."
        yield

    app = FastAPI(title="ChurnX API", version="1.0.0", lifespan=lifespan)
    origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    def service():
        if app.state.service is None:
            raise HTTPException(status_code=503, detail="Model unavailable; please try again later.")
        return app.state.service

    @app.middleware("http")
    async def measure(request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            LOGGER.exception("Request failed")
            response = JSONResponse(status_code=500, content={"detail": "Unable to process this request. Please try again."})
        current = getattr(app.state, "service", None)
        if current:
            with current.lock:
                current.monitor["requests"] += 1
                current.monitor["errors"] += int(response.status_code >= 500)
                current.monitor["total_latency_ms"] += (time.perf_counter() - start) * 1000
        return response

    @app.get("/health")
    def health():
        loaded = app.state.service is not None
        return JSONResponse(status_code=200 if loaded else 503, content={"status": "ok" if loaded else "unavailable", "model_loaded": loaded})

    @app.get("/model-info")
    def model_info():
        info = service().metadata
        return {key: value for key, value in info.items() if key != "reference_profile"}

    @app.post("/predict", response_model=PredictionOutput)
    def predict(customer: CustomerInput):
        return service().predict(customer)

    @app.get("/dashboard")
    def dashboard():
        return service().dashboard

    @app.get("/predictions")
    def history(limit: int = Query(default=50, ge=1, le=200)):
        with closing(sqlite3.connect(service().database)) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return {"predictions": [dict(row) for row in rows]}

    @app.get("/monitoring")
    def monitoring():
        current = service()
        with current.lock:
            stats = {**current.monitor, "risk_distribution": dict(current.monitor["risk_distribution"])}
        stats["average_latency_ms"] = round(stats["total_latency_ms"] / max(1, stats["requests"]), 2)
        stats["average_churn_probability"] = stats["probability_sum"] / max(1, stats["predictions"])
        return stats

    return app


app = create_app()
