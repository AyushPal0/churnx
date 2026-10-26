# ChurnX

Customer churn intelligence built with React/Vite, FastAPI and a reproducible scikit-learn pipeline. The application scores the real IBM Telco dataset and individual customer profiles, explains model sensitivity, and saves assessment history in SQLite.

## Measured results

Gradient Boosting was selected from Dummy, Logistic Regression, Decision Tree, Random Forest and Gradient Boosting using five-fold stratified cross-validation, then tuned within training data. On 1,409 held-out test customers: ROC-AUC **0.844**, PR-AUC **0.663**, recall **72.2%**, precision **56.5%**, F1 **0.634**. The validation-selected decision threshold is 0.35; display risk boundaries are 0.30 and 0.60.

## Local setup

Use Node 24+ and Python 3.12. On Windows PowerShell, `npm.cmd` avoids a disabled PowerShell npm script policy.

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.lock
npm.cmd ci --include=dev
```

Alternatively create the environment with `python -m venv .venv` and use its Python to run `-m pip install -r requirements.lock`. On Linux/macOS the virtual environment executable is `.venv/bin/python`.

The repository includes the source data and trained artifacts. Regenerate them when needed:

```powershell
.\.venv\Scripts\python.exe -m ml.train --download
```

Run the backend in one terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Run the frontend in a second terminal:

```powershell
npm.cmd run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to `http://127.0.0.1:8000`. If that port is occupied, choose another backend port and set `$env:CHURNX_API_PROXY='http://127.0.0.1:YOUR-PORT'` before starting Vite. For independent production hosting, set `VITE_API_URL` before the frontend build. The application displays connection errors when the backend is unavailable; it never substitutes hand-written prediction scores.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm.cmd run lint
npm.cmd test
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e
```

The browser suite starts its own servers on ports 18080/15173, exercises live inference, search/filtering, persisted history, errors and mobile layout, and writes screenshots into `reports/`. CI runs the same checks. Docker build/run requires a running daemon; see [DEPLOYMENT.md](./DEPLOYMENT.md).

The controlled `python -m scripts.benchmark` run completed 100 sequential prediction requests with 100% success and 18.83 ms p95 latency. This uses FastAPI TestClient, excluding network transit and model startup; the complete result is in `reports/benchmark.json`.

## Repository

- `ml/train.py`: source validation, EDA, train/validation/test splits, model comparison, tuning and serialization
- `backend/`: canonical input schema, model lifecycle, inference, history, monitoring and CORS
- `src/`: API-connected dashboard, customer table, prediction form, insights and model page
- `data/`: unchanged IBM CSV, cleaned copy and source provenance
- `models/`: saved preprocessing/classifier pipeline, metadata and dataset scores
- `reports/`: EDA, calibration, confusion matrix, split IDs, threshold sweep and UI screenshots
- `tests/`: backend integration, frontend contract and browser regression tests

## Interpretation and limitations

The data is a fictional customer snapshot, not a monthly event history. All-dataset scoring includes training rows; only held-out metrics estimate generalization. Local explanations measure sensitivity against the training reference rather than causal effects. Demographic subgroup metrics are recorded for review. Drift monitoring is manual; automatic retraining is outside V1. The sample API has no user accounts, so an access layer is needed before handling private customer profiles. Public deployment has not been provisioned.

Read [MODEL_CARD.md](./MODEL_CARD.md), [DATA_DICTIONARY.md](./DATA_DICTIONARY.md), [API.md](./API.md), [WORKPLAN.md](./WORKPLAN.md), and [PRD.md](./PRD.md) for details.

## Team

Amogh Sharma (S24CSEU1212), Ayush Pal (S24CSEU0352), Aditya Veer Singh (S24CSEU1195).
