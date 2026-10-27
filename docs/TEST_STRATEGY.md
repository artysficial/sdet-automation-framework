# Test strategy

## Scope

| In scope | Out of scope |
|---|---|
| Sauce Demo storefront: sign-in, catalogue, cart, checkout and order pricing | Visual and cross-browser testing beyond Chrome |
| ParaBank online bank: sign-in, accounts overview and funds transfer (UI + REST) | Load and performance testing |
| restful-booker API: booking lifecycle, authorisation, contract and error handling | Penetration testing beyond the detection-level security checks below |
| YouTube Data API v3: search, video, channel and contract checks | |
| Security: OWASP-aligned injection, XSS, access-control and header checks (see [SECURITY_TESTING.md](SECURITY_TESTING.md)) | |

All targets are public applications published for test-automation or security training. The suite runs once per
change and once nightly, keeps parallelism low, uses only non-destructive detection-level security payloads, and
cleans up the data it creates, so it does not burden the shared services.

## Risk-based priorities

| Risk | Why it matters | Coverage |
|---|---|---|
| Incorrect order total or tax | Customers are charged the wrong amount | Totals checked to the cent across 1-, 2- and 6-item baskets; display format checked separately |
| Unauthorised data changes | Anyone could alter or delete bookings | Update, partial update and delete attempted without a token, then the record is verified unchanged |
| Sign-in failures or unclear errors | Users locked out or confused | Valid, locked, wrong-password and empty-field cases with exact messages |
| Contract drift in the API | Integrations break silently | JSON Schema validation of booking payloads; status codes asserted per endpoint |
| Behaviour differing by account type | Some customers get a broken experience | Same journeys run for alternative accounts |

## Test levels and approach

- **UI (BDD, pytest-bdd + Selenium):** stakeholder-facing behaviour written as Gherkin scenarios, so a product owner
  can review coverage without reading code. Page objects hold all locators and waits; steps stay thin.
- **API (pytest + requests):** technical contracts kept as plain tests; they are about status codes and schemas,
  not business language.
- **Tags drive selection:** `smoke` (release gate), `regression`, `negative`, `contract`, plus functional areas.
  Example: `pytest -m smoke` for a fast pre-release check.

## Entry and exit criteria

**Entry:** target environments reachable; dependencies installed; test data generated per test.

**Exit (evaluated automatically by `tools/readiness_report.py`):**

1. Smoke suite passes in full.
2. No failures on critical paths (checkout and API contract tests).
3. Overall pass rate of at least 95%, excluding known defects.
4. Every known defect still reproduces as logged; an unexpected pass fails the run for re-verification.

The report recommends **Go**, **Go with conditions** (criteria met, known defects open) or **No-go**.

## Defect management

Defects are logged in [DEFECTS.md](DEFECTS.md) with steps to reproduce, expected and actual results, severity,
priority and impact, and each is linked to an automated reproduction test.

## Reporting

Every CI run produces:

- a release-readiness report (recommendation, exit criteria, defects, results by area);
- a detailed pytest-html report with screenshots and page URLs for failures;
- JUnit XML for CI tooling and a summary on the GitHub Actions run page.

Reports from `main` are published to GitHub Pages; every run's reports are kept as build artefacts for 30 days.
