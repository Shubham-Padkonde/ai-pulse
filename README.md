# AI Pulse client pilot

A role-aware AI habits assessment with private employee reports, protected team insights, and a **private one-week improvement plan**.

[Live reviewer demo](https://ai-pulse-reviewer.onrender.com/) · [Repository](https://github.com/Shubham-Padkonde/ai-pulse) · [Automated checks](https://github.com/Shubham-Padkonde/ai-pulse/actions/workflows/checks.yml)

This extends the inherited FastAPI/React application and retains its Git history. It supports a local synthetic-data demonstration and a single-service hosted reviewer demo with persistent storage. Real employee rollout still needs operational hardening and model validation. [Hosting and VS Code guide](docs/DEPLOYMENT.md).

The public demo uses live Google Gemini scoring and a separate PostgreSQL database. Use fictional answers only: its accounts are shared. The free website may take about a minute to wake after inactivity, and the free database expires 30 days after creation unless upgraded. The hosted report and plan were verified to survive a service restart on 28 October 2026.

## Run locally

Requirements: **Python 3.12+ (verified on 3.13), Node.js 24, npm and Git**.

From the repository root, on Windows, macOS or Linux:

~~~sh
python scripts/setup.py --demo
python scripts/run.py
~~~

On systems where Python is named python3, use that command instead.

Open **http://127.0.0.1:5173**. API documentation: **http://127.0.0.1:8000/docs**.

Setup creates an isolated Python environment, installs locked dependencies, generates a private random signing key, runs Alembic migrations and optionally seeds synthetic accounts. Existing databases are never reset. Running setup again is safe. Stop the local services with Ctrl+C. If a port is occupied, stop the conflicting local service before restarting.

The generated **backend/.env**, database and installed dependencies stay outside Git. The inherited signing key was public; the current application rejects it. Old history is retained, but that old key must never be used.

### Synthetic demo accounts

All demo passwords are **pulse123**. These accounts are deliberately public fixtures, suitable only for fictional demo data. On a shared public deployment, other visitors using the same account can view, change or delete its answers and plan.

| Account | Perspective |
| --- | --- |
| asha@northwind.test | Northwind admin; visible Engineering and Support teams, protected HR and Sales |
| priya@northwind.test | Support employee; personal report and three private activities |
| new@northwind.test | Support employee; empty on a fresh seed, ready to take or retake an assessment |
| dev@northwind.test | Engineering lead; more role and seniority questions |
| ravi@consult.test | Employee at Northwind, admin at Bluepeak |
| meera@bluepeak.test | Bluepeak admin; small departments remain protected |

The login page fills example credentials when a demo perspective is selected. It does not sign in automatically.

At the public deployment check, `new@northwind.test` had a completed live report of **3.50/5** and one completed policy-learning activity. Shared visitors can change this state; use Retake assessment for the full journey or the separate local rehearsal for a reproducible recording.

For a fresh recording fixture without changing the live configuration or database, run **python scripts/rehearse.py** after setup. It opens a separate synthetic workspace at **http://127.0.0.1:5174**, with exactly five completed Support employees. Each launch creates a new ignored database and always uses demo scoring. [Recording guide](docs/DEMO.md).

## What was wrong and what changed

| Inherited behaviour | Resulting behaviour | Evidence |
| --- | --- | --- |
| Caller-selected organization could cross the tenant boundary | The token establishes organization scope; every request checks current database membership and role. Foreign organization selection or dashboard access returns 403. | Tenant tests; Ravi demo account |
| Partial, duplicate or wrong-role submissions could produce misleading reports | The server requires each currently assigned question exactly once and validates every option and written answer. | Submission contract tests |
| Rows did not reliably establish completion | One versioned current assessment per membership; only fully scored completed assessments contribute. Retries do not create another person. | Lifecycle and idempotency tests |
| Small departments exposed information | Below five completed people, the API returns no score, exact count, level or risk breakdown. | 0/1/4/5/6 boundary tests |
| No employee deletion workflow | Current-company or all-membership deletion removes answers, reports and activities in one transaction. Late AI results cannot recreate them. | Delete and in-flight scoring tests |
| Model output could be loosely interpreted | Exact JSON fields, integer score 1–5, nonempty reason, four allowlisted risk labels; invalid output and provider failure leave scoring pending. | Parser and mocked provider tests |
| Weak password storage and a tracked signing secret | Salted Argon2 hashes, legacy upgrade on successful login, generated local secret, expiring scoped JWTs, bounded requests and local rate limits. | Authentication tests |
| Setup could damage data and lacked migrations | Explicit demo seed, nondestructive startup, fresh and legacy Alembic migration tests. | Migration tests |
| Results gave employees little help with the next step | A small private activity plan links observed gaps to practical exercises, target dates and completion. | Plan API and interface tests |

The questionnaire itself is retained. The product remains a self-reported diagnostic, not a validated measure of employee performance.

## The client request

**Small groups:** I chose suppression instead of combining departments into “Other teams.” Combining semantically different teams would be harder to interpret and could accidentally expose a small remainder.

- Completed **people** are counted, with one current assessment each.
- Each person's average has equal weight in the department average, regardless of how many role-specific questions they answered.
- All four risk categories appear in a fixed order for visible teams. An exact count requires at least five people with the signal and five without it; otherwise it says **Protected**. Zero and all-person counts are also protected. This prevents the department total from revealing a small complementary group.
- There is no company-wide score, participant total or risk total from which hidden departments could be reconstructed by subtraction.
- Department names remain visible; their protected numbers do not. The Unassigned row depends on organizational membership, so completing or deleting the first assessment cannot reveal participation by making that row appear or disappear.

**Deletion:** The employee can delete the current organization’s diagnostic or all their organizational diagnostics. Account and membership records remain so they can sign in again. Responses, the assessment and its plan are removed together, including legacy answers.

Fresh API reads exclude the deletion after the transaction commits. Already open views refresh every two seconds while visible and on focus; there is no server-side report cache. “Immediately” therefore means immediate backend exclusion, with a bounded UI refresh delay under normal network conditions. Previously saved screenshots and external provider retention cannot be revoked.

**Questions for the client before rollout:** Does “all my data” include account removal and identity records? Are department names acceptable? Is the two-second refresh window acceptable? What retention, backup-erasure and model-provider terms are required? What protection is needed against someone comparing many snapshots over time?

Suppression is not differential privacy and cannot guarantee anonymity against outside knowledge or repeated observations. Those residual risks require a client decision.

## Original feature: a private one-week improvement plan

Employees need something useful after receiving a score. The plan suggests up to three short activities from a curated catalog, with:

- the reason each activity was selected;
- an example appropriate to the employee’s role;
- practical steps and a clear completion criterion;
- an editable target date, initially one week away;
- completion and undo, visible only to the employee.

Rules prioritise data handling, review and policy gaps; a small practice workflow is the fallback. This is deliberately deterministic and inspectable. Another generative call would add cost and more opportunities for unreliable advice.

Completion is self-reported and **never raises the diagnostic score**. A changed retake replaces the old plan. Deleting the diagnostic removes the plan. Identical submissions reuse the current assessment and preserve its progress.

## AI behaviour and live mode

The default is clearly labelled **demo scoring**. Written answers receive a fixed sample score of 3, with an explanation saying it is a fixture. Seeded results are synthetic. Neither is presented as a real evaluation.

For live scoring, edit the private **backend/.env** locally, keeping its generated SECRET_KEY:

~~~dotenv
AI_MODE=live
LLM_API_URL=https://your-provider.example/v1/chat/completions
LLM_API_KEY=your-private-key
LLM_MODEL=your-model-identifier
~~~

Use the provider’s actual OpenAI-compatible chat-completions URL. Generic providers must support temperature and max_tokens. Google Gemini uses low reasoning effort, temperature 0 and a bounded 2,048-token budget so reasoning does not consume the small response allowance. Remote endpoints require HTTPS; local HTTP model servers are permitted. Restart the backend after configuration changes. Never put credentials in the frontend, Git, a recording or a chat message.

For the tested Google configuration, get a key from [Google AI Studio](https://aistudio.google.com/apikey), set LLM_API_URL to **https://generativelanguage.googleapis.com/v1beta/openai/chat/completions**, and set LLM_MODEL to **gemini-3.5-flash-lite**. Keep LLM_API_KEY only in your private backend environment. See [Google’s compatibility guide](https://ai.google.dev/gemini-api/docs/openai). Model availability and quota depend on the project. There is no automatic switch to another model after an error.

Only question text and the written answer are sent to the model. The request does not include the employee’s name, email or organization. Free text can still contain identifying information; the UI asks employees to remove it. The system rubric and user answer are separate messages. That separation is useful, but is not a guarantee against prompt injection or semantic misclassification.

Provider timeouts, rate limits, invalid envelopes and malformed content are handled without a fabricated score or raw provider error. Pending assessments are excluded from dashboards. Employees can retry or delete them. If the model configuration changed, a retake is required to preserve honest provenance.

Every assessment stores its questionnaire snapshot/version, rubric version, scoring mode and model. Enabling live mode does not relabel old synthetic reports.

### Evaluate a configured model

~~~sh
# No network calls; explains the available synthetic cases
python scripts/evaluate.py

# Windows
.venv\Scripts\python.exe scripts/evaluate.py --live --output work/live-evaluation.json

# macOS / Linux
.venv/bin/python scripts/evaluate.py --live --output work/live-evaluation.json
~~~

Live evaluation makes ten bounded synthetic requests; provider charges may apply. The cases cover ordinary use, disclosure, negation and prompt injection. Results show schema validity, expected score ranges and exact risk matches. A failed expectation exits nonzero.

**Live Google Gemini scoring was exercised on 28 October 2026.** Gemini 3.8 Flash returned capacity errors, so the demonstrated model is **gemini-3.5-flash-lite**. The initial run revealed two extra risk labels; a second run exposed a score-boundary ambiguity. After clarifying the rubric, version **pulse-rubric-v3** matched all ten score ranges and exact risk-label sets. These are iteratively tuned, author-written development cases, not an independent accuracy benchmark or evidence of fitness for employment decisions. All three sanitized runs are retained in [verification notes](docs/VERIFICATION.md). The provider contract and failure paths also have HTTP-mocked tests.

## Verification

A subsequent check used **eight fresh synthetic cases**, with expectations frozen before one run and no rubric changes or retries. All eight returned valid output, the expected score and the exact risk set, including a quoted instruction and four simultaneous risk signals. [The cases and results](docs/evaluations/gemini-flash-lite-fresh-v3.json) are included. This adds evidence beyond the tuned cases, but remains a small author-written check rather than independent validation.

~~~sh
python scripts/check.py
~~~

The suite uses isolated temporary databases and never resets the local demo database. It checks backend contracts, interface behaviour and a production frontend build.

At the verified build: **80 backend tests and 10 interface tests pass**, plus a separate real PostgreSQL integration test in CI. The Linux container build and startup smoke test also pass. Browser checks cover the local app and a public live-AI assessment with saved progress across a service restart; see [verification notes](docs/VERIFICATION.md) for scope and limits. A clean Windows clone and GitHub Actions on Linux also passed the setup and checks.

Dependency checks:

~~~sh
.venv\Scripts\python.exe -m pip_audit -r backend/requirements.txt
cd frontend
npm audit
~~~

The current scans reported no known vulnerabilities. This is a dated dependency check, not a security certification.

## Deliberate limits

- **Single-worker pilot:** SQLite locally, PostgreSQL on Render, synchronous bounded scoring, and a process-local rate limiter. Horizontal scale still needs a shared limiter, durable job queue and operational monitoring.
- **No real-user identity administration:** enterprise SSO, provisioning, account removal and immediate token revocation are deferred. Tokens expire after one hour; sign-out clears the browser session.
- **No arbitrary exports, filters or historical dashboards:** each would add a privacy surface.
- **No claim of AI calibration:** the original equal-weight rubric and maturity labels need client/domain validation. A high maturity score can coexist with risky behaviour.
- **Time-limited public demo:** Render provides HTTPS and private service variables. Its free database expires after 30 days and has no managed backups. Backup/restore and deletion policies, provider agreements and access auditing remain rollout requirements.
- **Container evidence is from Linux CI and Render:** the local Docker engine was unavailable; the Python/Node setup above is the verified local path.
- **Manual browser verification:** the interface tests use jsdom; they are not a cross-browser certification or a full accessibility audit.

## AI assistance and ownership

Codex assisted with analysis, implementation, tests, interface design and documentation. Public forks were inspected at the user's request to understand existing approaches; this implementation was developed from the original repository rather than copying a fork.

A concrete AI mistake: an initially strict date field rejected valid ISO dates sent by the browser. The API test caught that; date parsing was made permissive while completion remains a strict boolean. Another broad text edit accidentally applied the scoring rate limit twice; the exact-boundary test exposed it, and the duplicate was removed. These are reasons to verify generated code, not reasons to trust a polished interface.

The candidate must understand and be able to modify the submitted code. Start with [one assessment explained end to end](docs/EXPLAIN.md), then use [architecture](docs/ARCHITECTURE.md), [interview preparation and a timed coding exercise](docs/INTERVIEW.md), and the [under-five-minute recording guide](docs/DEMO.md).
