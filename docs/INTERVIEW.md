# Interview preparation

Use this to learn the implementation, not as a claim that you wrote or understand code you have not reviewed. The assessment allows AI assistance but expects a live explanation, modification and debugging session without AI.

## The opening explanation

“I inherited a working but untrusted application. I focused first on who can see which data, what counts as a completed assessment, and whether an AI failure could become a misleading result. Then I implemented the client’s small-group and deletion requirements. My added feature gives the employee a private, practical plan for the following week.”

Be precise about readiness: the local pilot and deterministic failure paths are verified. Live Gemini scoring and ten development cases were exercised. Independent model accuracy and production operations still need validation.

## The six ideas to explain in your own words

**Authentication and authorization differ.** Authentication identifies the signed-in user. Authorization checks whether that user has the necessary role in the selected company. Hiding a navigation link is convenience; the API must still reject the request.

**Answers are not completed assessments.** Six answer rows could be an incomplete set, duplicates or invalid options. The server checks the exact assigned question set, then publishes only after every required answer has a valid score.

**Privacy belongs at the API boundary.** Hiding a score in React would still expose it in the network response. The backend returns null for protected fields. No company total is published because subtraction could reveal a hidden group.

**A failed model call is an operational failure, not a score.** Giving a default 3 would silently invent evidence and distort dashboards. Pending state saves the employee’s work without pretending to finish the assessment.

**Deletion must cover derived data and races.** The report and plan derive from answers. They must disappear too. An AI request already in flight must check that its exact assessment and lease still exist before saving.

**A completed activity is not proof of improved capability.** The plan is useful for learning, but its checkboxes do not change diagnostic scores. That prevents an easy but dishonest “growth” metric.

## A 45-minute code tour

1. **10 minutes:** read models.py and auth.py. Draw User → Membership → Assessment → Responses/Actions. Explain why role belongs to a membership.
2. **10 minutes:** follow diagnostic.submit → save_submission → score_saved. Locate validation, transaction commit, network call and final conditional update.
3. **10 minutes:** read dashboard.py and privacy.py. Manually work out a team with four people, then five. Explain why five answers from one person do not qualify.
4. **5 minutes:** read actions.py and reports.update_action. Explain activity selection and ownership.
5. **10 minutes:** run the tests, then read the five-to-four deletion test and invalid-output test until you can describe each assertion.

## Likely interview questions

**Why keep SQLite?** It is adequate for a small local pilot and makes setup easy. Writes are short and model calls happen outside transactions. Multiple application workers, sustained load and shared operations would justify PostgreSQL and a job queue. There is no production-scale claim.

**Why not use a background queue now?** It adds infrastructure, delivery semantics and monitoring. The pilot uses bounded synchronous scoring with a recoverable state and explicit retry. A queue becomes useful when long jobs, throughput or durable automatic retries are required.

**What did the live test change?** Gemini 3.8 Flash returned capacity errors, so the demonstrated model is Gemini 3.5 Flash-Lite. Initial results over-reported two risks. Clarifying independent risk evidence fixed those; the next run exposed a regular-use scoring ambiguity. The final rubric makes frequency and review explicit and passed the ten development cases. The rubric version is stored with each assessment. These tuned cases do not establish general accuracy.

**Does a valid JSON response mean the AI is correct?** No. Schema checks prevent malformed or out-of-range output. They cannot establish semantic accuracy. The live smoke cases include negation and injection; a larger independently labelled set and domain review are still needed.

**What does idempotent mean here?** Resubmitting the same normalized answers under the same questionnaire and scorer configuration reuses the existing assessment. It does not add another completed person or reset activity progress.

**Why a revision and a scoring lease?** The revision prevents a stale submission from overwriting another request. The lease distinguishes an active scoring attempt from a newer replacement attempt after an interruption.

**Is suppression anonymity?** No. It removes direct small-group outputs and the simple total-subtraction attack. Repeated snapshots and outside knowledge remain risks. Describe the limit openly.

**What did the final code review catch?** Two privacy gaps: a risk count could expose a small complement, and an Unassigned row appeared only after someone completed an assessment. Five flagged out of six reveals the remaining one, so exact counts now require five people on both sides. The Unassigned row now depends on membership. Regression tests failed before the fixes and passed afterwards; the interface says Protected rather than claiming a 0–4 range.

**Did you test beyond cases used to tune the prompt?** Yes. Eight fresh synthetic cases had their expectations frozen before one run with the unchanged v3 rubric. All eight matched their scores and exact risks, including a quoted instruction and multiple risks together. That is useful extra evidence, but the cases are still author-written and too small to establish real-world accuracy.

**How immediate is deletion?** After the deletion transaction commits, new API reads exclude the assessment. Existing browser views normally update within two seconds plus network time. The system cannot take back screenshots.

**Can an admin read an employee’s plan?** No API endpoint grants that capability. The personal route derives the owner from the authenticated membership; an action from someone else returns 404.

**How did AI get something wrong?** The initial strict date field rejected legitimate browser ISO-date strings. A test exposed the mismatch; only date parsing was relaxed. A broad edit also doubled a rate-limit charge. An exact-boundary test caught it. Explain the fix rather than blaming the tool.

**What would you do next?** Validate the selected model with domain experts; agree on privacy and retention; add real identity provisioning; test deployment, backups and restoration; add shared rate limiting and durable scoring jobs only as load requires.

## Practice a small change without AI

Try these in order, inspecting the relevant tests before editing:

- Change the title of one activity. Find the source catalog and verify the plan screen.
- Add a new activity-selection rule for a low review score. Predict which tests need a new scenario.
- Change the privacy threshold from five to six. Update the boundary test first; remember configuration, risk bands and UI wording must stay consistent.
- Add an optional field to an activity only after deciding whether it belongs in storage. If stored, add a new migration.

Do not leave practice changes in the submission unless they are intentional and verified.

## Debugging exercise

Read the test for invalid model output. Follow the response from the fake provider to strict parsing, pending state and dashboard suppression. Then follow a successful retry.

For an API error, inspect the HTTP status and sanitized detail first. For a missing team result, check completion status and threshold before changing the UI. Never “fix” a pending report by assigning a default score.
