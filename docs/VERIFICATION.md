# Verification record

Local verification on **28 October 2026**, using Windows, Python 3.13 and Node.js 24.

## Automated checks

The final local check command is **python scripts/check.py**.

| Check | Result |
| --- | --- |
| Backend tests | 66 passed |
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
- mobile navigation and page width;
- deletion dialog begins with its destructive button disabled;
- the first-time assessment flow through all six questions and submission; its completed report was confirmed in the API and in the browser after signing out and in again.

The multi-company browser check passed: Ravi sees the Bluepeak admin dashboard, then loses the leadership navigation when switching back to Northwind as an employee.

Screenshots in this directory show synthetic data. Browser deletion was not used to erase the main demonstration fixture; the isolated API tests verify the actual deletion and five-to-four boundary.

## Limits of this evidence

A passing API test is not a browser test. A mocked provider is not a real model evaluation. The interface suite uses jsdom, and the manual browser check is not a complete accessibility audit or coverage of every browser.

No live model credentials were available. There is no measured live-model semantic accuracy, concurrency load benchmark, production deployment test, backup-restore exercise, or container execution result.

The included GitHub workflow ran the same setup and check commands successfully on Linux: [verified run](https://github.com/Shubham-Padkonde/ai-pulse/actions/runs/40649645631).
