# Deployment

## Selected setup: Vercel frontend + Render Free API

The root `vercel.json` fixes the Vite framework, dev-dependency installation, build command and `dist` output. `.vercelignore` excludes the Python backend, model artifacts, datasets, local environments and generated reports from CLI frontend uploads. No Python API is deployed to Vercel in this setup.

1. Import `AmoghxAnubis/CHURNX-` into Vercel, using the repository root and the settings in `vercel.json`. This supplies the real frontend origin. Its interface can be deployed first, but will show the service as unavailable until the next steps are finished.
2. Connect the same GitHub repository to a Render Blueprint using `render.yaml`. Select the free service and supply `ALLOWED_ORIGINS` with the exact Vercel frontend HTTPS origin, without a trailing slash. The Blueprint uses Python 3.12.13, the pinned requirements lock, and the existing trained artifacts; it does not retrain during deployment.
3. Wait for Render's `/health` to return 200 with `model_loaded: true`. Copy the actual assigned Render API origin; the service name does not guarantee that a particular `onrender.com` hostname is available.
4. In the Vercel project, set `VITE_API_URL` to that Render origin for Production (and Preview if desired), then redeploy. This URL is public configuration, not a secret. Never set it to localhost in a cloud deployment.
5. Verify the Overview, customer search, individual prediction, history, insights and model metadata through the production frontend. If using Vercel preview domains, add those exact origins to Render's comma-separated `ALLOWED_ORIGINS`; an allowed production domain does not automatically permit every preview hostname.

Render Free sleeps after 15 minutes without inbound traffic and may take about a minute to wake. Initial dashboard loading therefore waits up to 90 seconds before offering retry. The SQLite database is deliberately placed at `/tmp/churnx/predictions.db`: history survives normal requests while the instance runs, but resets on sleep, restart or redeployment. Model files shipped in the repository remain available. Persistent history requires upgrading the backend storage or adding an external database later.

Official references: [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite), [FastAPI on Render](https://render.com/docs/deploy-fastapi), [Render free limits](https://render.com/docs/free).

## Backend container

From the repository root:

```bash
docker build -t churnx-api .
docker run --rm -p 8000:8000 -e PORT=8000 -e ALLOWED_ORIGINS=https://YOUR-FRONTEND-DOMAIN -v churnx-history:/app/runtime churnx-api
```

The image runs as a non-root user and includes the serialized pipeline and metadata. The `PORT` variable is honored for container platforms. Model artifacts must be generated before building. A named volume preserves SQLite history; use one instance for this SQLite demonstration deployment. Configure a persistent disk on a hosting platform for history that survives redeployment.

Confirm `GET https://YOUR-API-DOMAIN/health` returns 200 before connecting the frontend. This workspace has no running Docker daemon, so the image definition is supplied but a local container build/run has not been verified.

## Frontend

Deploy the root Vite project to Vercel or another static host. Build command: `npm ci --include=dev && npm run build`; publish directory: `dist`. Set `VITE_API_URL=https://YOUR-API-DOMAIN` before building, then rebuild. Vite embeds the variable at build time. The local `/api` proxy is development-only and is not included in static hosting.

Update backend `ALLOWED_ORIGINS` to the exact frontend HTTPS origin, restart the API, then verify the Overview data, customer filtering, model metadata, and an individual prediction in the deployed application. Public deployment URLs have not been provisioned in this workspace; a hosting account and selected destination are required.

## Operation

Check `/monitoring` for process-level request count, server errors, latency and risk distribution. Review drift manually by comparing new profile distributions with the training data; automated drift detection and retraining remain future work. Retraining is a deliberate `python -m ml.train` operation, followed by metric review, model version change and service restart. Never replace the artifact solely because a training run finished.
