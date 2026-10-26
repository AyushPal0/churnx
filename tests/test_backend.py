import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import ROOT, create_app
from backend.schema import CustomerInput, RAW_COLUMNS, risk_level
from ml.train import load_data


@pytest.fixture
def payload():
    return {"gender": "Female", "senior_citizen": 0, "partner": "Yes", "dependents": "No", "tenure": 12,
            "phone_service": "Yes", "multiple_lines": "No", "internet_service": "Fiber optic", "online_security": "No",
            "online_backup": "Yes", "device_protection": "No", "tech_support": "No", "streaming_tv": "Yes", "streaming_movies": "Yes",
            "contract": "Month-to-month", "paperless_billing": "Yes", "payment_method": "Electronic check", "monthly_charges": 89.5, "total_charges": 1074.0}


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(database=tmp_path / "predictions.db")) as current:
        yield current


def test_prediction_matches_saved_pipeline_and_persists(client, payload, tmp_path):
    assert client.get("/health").json() == {"status": "ok", "model_loaded": True}
    model = client.get("/model-info").json()
    pipeline = joblib.load(ROOT / "models/churnx_pipeline.joblib")
    frame = pd.DataFrame([CustomerInput(**payload).raw_row()], columns=model["features"])
    expected = pipeline.predict_proba(frame)[0, 1]
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["churn_probability"] == pytest.approx(expected)
    assert result["prediction"] == int(expected >= model["threshold"])
    assert result["risk_level"] == risk_level(expected)
    assert result["top_factors"]
    assert "training reference" in result["top_factors"][0]
    history = client.get("/predictions").json()["predictions"]
    assert len(history) == 1 and history[0]["id"] == result["prediction_id"]
    stats = client.get("/monitoring").json()
    assert stats["predictions"] == 1
    assert sum(stats["risk_distribution"].values()) == 1
    assert stats["average_churn_probability"] == pytest.approx(expected)


@pytest.mark.parametrize("changes", [
    {"tenure": -1}, {"monthly_charges": -1}, {"total_charges": -10}, {"contract": "Monthly"},
    {"payment_method": "Cash"}, {"senior_citizen": 2}, {"usageFrequency": 10},
    {"phone_service": "No"}, {"internet_service": "No"}, {"tenure": 1.5},
])
def test_reject_invalid_input(client, payload, changes):
    assert client.post("/predict", json={**payload, **changes}).status_code == 422
    assert client.get("/predictions").json()["predictions"] == []


def test_missing_and_non_finite_input(client, payload):
    del payload["tenure"]
    assert client.post("/predict", json=payload).status_code == 422
    payload["tenure"] = 12
    payload["monthly_charges"] = "Infinity"
    assert client.post("/predict", json=payload).status_code == 422


def test_missing_model_fails_honestly(tmp_path, payload):
    with TestClient(create_app(model_path=tmp_path / "absent.joblib", database=tmp_path / "predictions.db")) as current:
        assert current.get("/health").status_code == 503
        response = current.post("/predict", json=payload)
        assert response.status_code == 503
        assert "traceback" not in response.text.lower()


def test_cors(client):
    headers = {"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"}
    assert client.options("/predict", headers=headers).headers["access-control-allow-origin"] == "http://localhost:5173"
    headers["Origin"] = "https://untrusted.example"
    assert "access-control-allow-origin" not in client.options("/predict", headers=headers).headers


def test_database_connections_close_after_requests(tmp_path, payload):
    database = tmp_path / "history.db"
    with TestClient(create_app(database=database)) as current:
        assert current.post("/predict", json=payload).status_code == 200
        assert len(current.get("/predictions").json()["predictions"]) == 1
    # Windows cannot rename a SQLite file that is still held open by our connections.
    renamed = database.rename(tmp_path / "closed-history.db")
    assert renamed.exists()


def test_dataset_schema_and_split_integrity():
    data = load_data(ROOT / "data/raw/Telco-Customer-Churn.csv")
    assert len(data) == 7043
    assert len(RAW_COLUMNS) == 19
    assert (data.loc[data.tenure == 0, "TotalCharges"] == 0).all()
    splits = json.loads((ROOT / "reports/splits.json").read_text())
    partitions = [set(value) for value in splits.values()]
    assert not partitions[0] & partitions[1] and not partitions[0] & partitions[2] and not partitions[1] & partitions[2]
    assert set.union(*partitions) == set(data.customerID)
    metadata = json.loads((ROOT / "models/metadata.json").read_text())
    assert "customerID" not in metadata["features"] and "Churn" not in metadata["features"]
    assert len(metadata["comparison"]) >= 4
    assert all(metadata["performance_gates"].values())
    assert metadata["metrics"]["roc_auc"] > metadata["baseline_metrics"]["roc_auc"]
    pipeline = joblib.load(ROOT / "models/churnx_pipeline.joblib")
    assert list(pipeline.named_steps) == ["preprocessing", "classifier"]
    assert pipeline.named_steps["preprocessing"].named_transformers_["numeric"].named_steps["scale"].n_samples_seen_ == len(splits["train"])


def test_dashboard_computed_from_model(client):
    dashboard = client.get("/dashboard").json()
    assert dashboard["records"] == len(dashboard["customers"]) == 7043
    assert sum(row["count"] for row in dashboard["groups"]["Contract"]) == 7043
    assert len({row["id"] for row in dashboard["customers"]}) == 7043
    assert all(np.isfinite(row["churnProbability"]) and 0 <= row["churnProbability"] <= 100 for row in dashboard["customers"])
    assert client.get("/predictions?limit=100000").status_code == 422


@pytest.mark.parametrize("probability, expected", [(0, "LOW"), (.2999, "LOW"), (.3, "MEDIUM"), (.5999, "MEDIUM"), (.6, "HIGH"), (1, "HIGH")])
def test_risk_boundaries(probability, expected):
    assert risk_level(probability) == expected
