# ChurnX PRD implementation and iteration log

The first frontend pass established the interface. Continuation completes the local ML product: real data → reproducible training → serialized pipeline → FastAPI → dashboard. External deployment is tracked independently because it needs a hosting destination.

## Iteration loop

For each slice: inspect the PRD contract, implement, verify, review the evidence, and repair failures before proceeding. No dedicated Ralph-loop runner was present in the workspace; this is the explicit implementation/review loop used here.

## Data and ML

- [x] Preserve and validate the IBM source CSV and record its SHA-256.
- [x] Clean blank TotalCharges for zero-tenure customers without changing raw data.
- [x] Produce EDA groups, distributions, correlations and visualizations before training.
- [x] Use disjoint stratified train/validation/test splits and save IDs.
- [x] Fit imputation, scaling and encoding only within training folds.
- [x] Compare Dummy, Logistic Regression, Decision Tree, Random Forest and Gradient Boosting using five-fold CV.
- [x] Tune the selected family with GridSearchCV on training data.
- [x] Select the classification threshold on validation data and evaluate held-out test data.
- [x] Serialize the full pipeline with measured metrics, provenance and version.
- [x] Record permutation importance, local sensitivity method, calibration/Brier score and demographic subgroup metrics.

## Backend

- [x] Load the trusted model once at startup.
- [x] Implement `/health`, `/model-info`, `/predict`, `/dashboard`, `/predictions`, and `/monitoring`.
- [x] Enforce categories, finite/range checks, required fields and service dependencies.
- [x] Separate configurable display risk bands from the tuned classification threshold.
- [x] Use explicit CORS origins and friendly unavailable/inference errors.
- [x] Persist assessment summaries in SQLite without storing submitted customer profiles.
- [x] Verify inference parity with the saved model, invalid requests, model absence, CORS, splits, and history.

## Frontend

- [x] Connect every view to real scores, insight groups and measured model metadata.
- [x] Remove fabricated customer records, prediction rules, feature importances and evaluation results.
- [x] Send canonical snake_case API payloads and use the backend's classification decision.
- [x] Synchronize phone/internet dependent categories.
- [x] Add pending, error, offline, retry and empty states.
- [x] Add customer search, risk filter, sorting and pagination for 7,043 records.
- [x] Show persisted prediction history and separate risk/classification semantics.
- [x] Use USD charges and accessible navigation labels at narrow widths.

## Delivery and checks

- [x] Lock backend dependencies and provide environment examples.
- [x] Add a non-root Python Dockerfile and independent frontend deployment instructions.
- [x] Add CI for lint/build, contract tests, API tests and browser tests.
- [x] Add README, model card, dictionary, API documentation and dataset provenance.
- [x] Frontend lint, contract tests and production build pass.
- [x] Backend integration/data tests pass (23 tests, including explicit database connection closure).
- [x] All three browser regression tests pass; desktop/mobile screenshots visually reviewed.
- [x] Controlled 100-request API benchmark passes: 100% success, 18.83 ms p95 (excluding network transit and startup).
- [ ] Verify a Docker build/run (daemon unavailable in this workspace).
- [ ] Provision public frontend/backend hosting and verify deployed CORS/prediction (hosting destination required).

## Selected deployment configuration

- [x] User selected Vercel for the frontend and Render Free for the API.
- [x] Add explicit Vercel build settings and exclude Python/local artifacts from frontend CLI uploads.
- [x] Add a free Render Blueprint with health checks, locked dependencies, Python 3.12 and temporary SQLite history.
- [x] Allow 90 seconds for initial API cold-start connection and explain the waiting state in the dashboard.
- [ ] Connect Vercel/Render accounts, obtain real deployment domains, set API URL/CORS, and verify production.

## Measured model outcome

Gradient Boosting, classification threshold 0.35. Held-out ROC-AUC 0.84398, recall 0.72193 and F1 0.63380. All three PRD gates pass. The source has 7,043 customers; the trained model scores 964 at high risk and estimates average dataset risk of approximately 26.4%.

## Browser review

Desktop and 390-pixel mobile Overview screenshots were captured and visually reviewed, along with the completed prediction view. All browser tests pass: live scores, filtering/search, model and insight pages, real prediction parity, reload-persisted history, dependent service fields, offline/retry/error handling, and mobile viewport fit. A Windows benchmark exposed lingering SQLite handles; explicit connection closure was added and verified by a database-rename regression test.
