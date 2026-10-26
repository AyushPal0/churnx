# ChurnX API

Start from the repository root with `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`. Interactive OpenAPI documentation is at `/docs`.

| Method and path | Behavior |
|---|---|
| `GET /health` | 200 with `status: ok` and `model_loaded: true`; 503 when model artifacts cannot load |
| `GET /model-info` | Version, model family, real test metrics, CV comparison, training metadata and risk bands |
| `POST /predict` | Validated customer profile → model probability, risk, classification and local sensitivity factors |
| `GET /dashboard` | Scores for all 7,043 dataset records and measured historical insight groups |
| `GET /predictions?limit=50` | Most recent persisted assessment summaries; limit 1–200 |
| `GET /monitoring` | Process request/error counters, average request latency, risk distribution and probability summary |

## Prediction request

```json
{
  "gender": "Female",
  "senior_citizen": 0,
  "partner": "Yes",
  "dependents": "No",
  "tenure": 12,
  "phone_service": "Yes",
  "multiple_lines": "No",
  "internet_service": "Fiber optic",
  "online_security": "No",
  "online_backup": "Yes",
  "device_protection": "No",
  "tech_support": "No",
  "streaming_tv": "Yes",
  "streaming_movies": "Yes",
  "contract": "Month-to-month",
  "paperless_billing": "Yes",
  "payment_method": "Electronic check",
  "monthly_charges": 89.5,
  "total_charges": 1074
}
```

See `DATA_DICTIONARY.md` for allowed categories and service dependency rules. All fields are required. Invalid, missing, extra, non-finite, negative, or contradictory inputs return 422 before inference.

## Response

`churn_probability` is a number in [0,1]; `churn_percentage` is its percentage. `prediction` is 0 or 1 using the saved validation threshold. `risk_level` is LOW/MEDIUM/HIGH using separately saved risk bands. `model_version` identifies the exact artifact version. `top_factors` contains sensitivity-based explanations; `explanation_method` describes their limitations. `prediction_id` identifies the persisted assessment summary.

The service stores an opaque ID, UTC time, probability, risk, decision, and model version. It does not persist the submitted profile. SQLite failures return a generic 500 rather than reporting an assessment as saved. Missing models return 503; inference exceptions return a generic 500 without a Python traceback in the HTTP response.

## Configuration

`MODEL_PATH` selects the trusted joblib file. `metadata.json` and `dashboard.json` must be adjacent. `DATABASE_PATH` selects the SQLite database (default `runtime/predictions.db`). `ALLOWED_ORIGINS` is a comma-separated explicit frontend origin list. The server does not load `.env` automatically; export variables in the process environment. CORS is not authentication. The sample-data demonstration API has no user accounts; place it behind an access gateway before using private customer data.
