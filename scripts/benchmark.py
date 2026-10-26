"""Controlled API benchmark, excluding network transit and model startup."""
import json
import statistics
import tempfile
import time
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import ROOT, create_app
from backend.schema import RAW_COLUMNS
from ml.train import load_data


def main():
    row = load_data(ROOT / "data/raw/Telco-Customer-Churn.csv").iloc[0].to_dict()
    payload = {key: row[value] for key, value in RAW_COLUMNS.items()}
    times, statuses = [], []
    with tempfile.TemporaryDirectory(prefix="churnx-benchmark-") as directory:
        with TestClient(create_app(database=Path(directory) / "history.db")) as client:
            client.post("/predict", json=payload)  # Warm-up.
            for _ in range(100):
                start = time.perf_counter()
                response = client.post("/predict", json=payload)
                times.append((time.perf_counter() - start) * 1000)
                statuses.append(response.status_code)
    result = {"requests": len(statuses), "success_rate": statuses.count(200) / len(statuses),
              "mean_ms": round(statistics.mean(times), 2), "p95_ms": round(sorted(times)[94], 2),
              "max_ms": round(max(times), 2), "scope": "Sequential local FastAPI TestClient requests, excluding model startup and network transit"}
    (ROOT / "reports/benchmark.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["success_rate"] <= .99 or result["p95_ms"] >= 500:
        raise SystemExit("Controlled demo performance targets not met")


if __name__ == "__main__":
    main()
