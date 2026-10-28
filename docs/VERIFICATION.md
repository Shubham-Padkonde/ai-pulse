# Verification record

Local verification on **28 October 2026**, using Windows, Python 3.13 and Node.js 24.

## Automated checks

The final local check command is **python scripts/check.py**.

| Check | Result |
| --- | --- |
| Backend tests | 68 passed |
| React interface tests in jsdom | 6 passed |
| Production frontend build | Passed |
| Python runtime dependency audit | No known vulnerabilities reported |
| npm dependency audit | No known vulnerabilities reported |
| Fresh database migration and repeat upgrade | Passed |
| Upgrade from a legacy database while retaining its answer | Passed |
| Live evaluation dry run | Lists ten cases; makes no network calls |
| Fresh-clone setup with a new environment and demo database | Passed; all tests and production build also passed |
| GitHub Actions on Ubuntu, Python 3.13 and Node 24 | Passed |

The backend test runner currently emits a Starlette warning that its httpx-based test client will be replaced. Tests pass; a test-client dependency migration is deferred.

## What the tests actually establish

- A signed-in user cannot select an unowned organization or query another company’s dashboard.
- Employee permissions remain narrower than admin permissions, including for a user in two companies.
- Empty, partial, duplicate, wrong-role and invalid-choice submissions cannot replace existing valid data.
- Counts reflect completed people. Four people are protected; five qualify. Repeated submission does not add another person.
- Deletion removes answers and activities, changes dashboard eligibility and is safe to repeat.
- Deletion during model scoring cannot resurrect the deleted assessment.
- A stale scoring worker cannot overwrite a newer lease, and a stale membership revision cannot replace a newer submission.
- A provider error cannot turn into a fabricated score. Invalid JSON, types, bounds, duplicate keys and unknown flags are rejected.
- Mocked HTTP timeout, 429, 500 and invalid-envelope paths produce safe error categories.
- Completion and target-date updates remain private and do not change assessment scores.
- A changed scorer configuration cannot silently relabel pending or synthetic data.
- Password hashes are salted, legacy passwords upgrade after successful login, and request validation does not echo secrets.
- Login and scoring requests are rate limited; oversized request bodies are rejected.
- Interface tests cover the assessment flow, pending display, privacy display, activity completion, typed deletion confirmation and API errors.

## Browser verification scope

The local app was checked through the in-app Chromium browser at desktop and phone-sized layouts:

- leadership login, organization selection and protected dashboard;
- employee report and plan, saved completion after page reload, unchanged report score;
- mobile navigation and page width, including a 314-pixel report and plan with no sideways overflow;
- deletion dialog begins with its destructive button disabled;
- the first-time assessment flow through all six questions and submission; its completed report was confirmed in the API and in the browser after signing out and in again.

The multi-company browser check passed: Ravi sees the Bluepeak admin dashboard, then loses the leadership navigation when switching back to Northwind as an employee.

Browser checks used synthetic data. Browser deletion was not used to erase the main demonstration fixture; the isolated API tests verify the actual deletion and five-to-four boundary.

## Limits of this evidence

A passing API test is not a browser test. A mocked provider is not a real model evaluation. The interface suite uses jsdom, and the manual browser check is not a complete accessibility audit or coverage of every browser.

There is no independent live-model semantic accuracy measurement, concurrency load benchmark, production deployment test, backup-restore exercise, or container execution result. The live development checks below must not be presented as a held-out accuracy benchmark.

The included GitHub workflow ran the same setup and check commands successfully on Linux: [verified run](https://github.com/Shubham-Padkonde/ai-pulse/actions/runs/40649645631).

## Live Gemini development checks — 28 October 2026

The private local key authenticated successfully. Gemini 3.8 Flash timed out and then returned HTTP 503 high-demand errors. Gemini 3.5 Flash-Lite returned a valid synthetic score; the application was configured explicitly for that model. Model failures never trigger a silent model change.

| Rubric | Valid outputs | Score ranges matched | Exact risk sets matched | Evidence |
| --- | --- | --- | --- | --- |
| v1 | 10/10 | 10/10 | 8/10 | [Initial run](evaluations/gemini-flash-lite-v1.json) |
| v2 | 10/10 | 9/10 | 10/10 | [Risk clarification](evaluations/gemini-flash-lite-v2.json) |
| v3 | 10/10 | 10/10 | 10/10 | [Frequency/review clarification](evaluations/gemini-flash-lite-v3.json) |

The original rubric over-labelled confidential sharing when only customer records were described, and unreviewed output when an answer explicitly said it was read. The revised rubric treats each risk separately. The second run scored a regular, checked workflow too low; v3 makes that boundary explicit. The final request uses low reasoning effort, temperature 0 and a 2,048-token limit. This reduces sampling variation but does not guarantee deterministic results.

These are the same ten author-written cases used during development. The final 10/10 is a calibration result, not unbiased accuracy evidence. No employee data or API key is included in the saved result files.

The browser journey also passed against the real provider: a newly created synthetic employee in a separate local test workspace answered all six questions. The saved report showed a 3.33 average, the written answer received 4/5 with a relevant review-based explanation, and only the expected policy-awareness risk appeared. The private plan selected the policy-learning activity. The report persisted after reload with live mode, Gemini 3.5 Flash-Lite and rubric v3 recorded. Existing synthetic reports stayed labelled as samples.
