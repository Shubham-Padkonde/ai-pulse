# Hosting the reviewer demo

The root Dockerfile builds React and serves its static output through the same
FastAPI process as the API. An empty `VITE_API_URL` means same-origin requests;
no public browser calls localhost. The build contains a shared-account notice.
This is a synthetic reviewer demo, not a real employee deployment.

## Railway setup

Use one service, one replica and one persistent volume mounted at `/data`.
The volume is required: Railway's ordinary application filesystem is ephemeral.
The SQLite database is `sqlite:////data/aipulse.db`. Never upload a local database.
Check the account's current credits and spending limits before deploying. Free
trial credits expire; the public link is not a promise of unlimited free hosting.

Set these **runtime service variables**, not frontend build variables:

| Name | Value |
| --- | --- |
| `DATABASE_URL` | `sqlite:////data/aipulse.db` |
| `SECRET_KEY` | A new random secret of at least 32 characters, kept stable across restarts |
| `SEED_DEMO` | `true`; only creates fictional accounts when the database has no users |
| `AI_MODE` | `live` for real provider scoring, or `mock` for labelled fixtures |
| `LLM_API_URL` | Provider's HTTPS chat-completions endpoint |
| `LLM_MODEL` | A model available to the provider account |
| `LLM_API_KEY` | Saved only in the hosting provider's secret settings |
| `CORS_ORIGINS` | The exact public HTTPS origin |

Railway supplies `PORT`. The image sets `STATIC_DIR=/app/web`. Startup validates
configuration, runs Alembic, seeds only if explicitly requested, then starts one
Uvicorn worker. A missing secret, invalid static build or failed migration stops
startup rather than presenting a broken app. `/health` is the deployment check.

Deploy the repository root, not `frontend/` or `backend/`. Generate a Railway
domain pointing at the service's HTTP port. Keep the volume attached when
restarting or redeploying. `SEED_DEMO=true` never resets existing answers.

## Verify before sharing

1. Open the public HTTPS link and confirm the public-demo notice is visible.
2. Sign in as `new@northwind.test` / `pulse123`, choose Northwind and complete
   an assessment using fictional answers. Confirm the report says Live AI when
   live mode is selected. The pre-seeded historical reports remain labelled demo.
3. Change an improvement-plan activity. Restart the service and sign in again;
   the report and activity state must remain. Keep the signing secret unchanged.
4. Use the admin account to check protected departments. Use a separate browser
   context for the employee account. Check deletion and a fresh assessment.
5. Requests for `/.env`, `/aipulse.db` and `/app/config.py` must return 404.

## Deliberate limits

- Demo credentials are public. Anyone using the same account can view, replace
  or delete its data. Use fictional answers only. Private employee accounts are
  required before using this with real people.
- Live written answers go to Google when its endpoint is configured. Never put
  customer information, company secrets or personal data into this public demo.
- The existing rate limit is per process, not a durable provider spending cap.
  Apply provider quotas and monitor usage. A quota/provider error leaves a saved
  pending assessment with an explicit retry; it never fabricates a live score.
- SQLite plus a mounted volume is appropriate for this small, single-instance
  demonstration. Multiple replicas need a shared database and distributed limits.
- The container runs as root to write Railway's root-owned mounted volume.
  Before real rollout, configure volume ownership and run as an unprivileged
  user, add managed backups/restore checks, monitoring, identity provisioning,
  retention rules and an independently labelled model evaluation.
- Deletion applies to the live database. Backups and external model retention
  require a separate retention policy; do not claim deletion covers those copies.

## VS Code

Open the repository folder, complete setup once, and use **Ctrl+Shift+B** to run
**AI Pulse: Run local app**. The integrated task runs the API on 8000 and Vite on
5173. Stop this task before starting a second copy. **Terminal > Run Task** also
provides **AI Pulse: Check project** and **AI Pulse: Fresh rehearsal** (8001/5174).
The local live database and the rehearsal database are separate from hosting.

Official references: [Railway volumes](https://docs.railway.com/volumes/reference),
[Dockerfiles](https://docs.railway.com/builds/dockerfiles),
[pricing](https://railway.com/pricing).
