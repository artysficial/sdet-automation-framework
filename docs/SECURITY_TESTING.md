# Security testing

The security suite applies a small set of OWASP-aligned checks as part of normal QA regression. It is
**defensive**: the goal is to confirm that protections hold and to surface misconfigurations, not to exploit systems.

## Authorization boundary

Every target is an application that is **published specifically for testing and training**, and is tested only in
ways its providers intend:

| Target | Nature | How it is used here |
|---|---|---|
| [ParaBank](https://parabank.parasoft.com) | Parasoft's public demo bank | Non-destructive negative checks: injection must not bypass auth or leak errors; input must be encoded; recommended security headers are verified |
| [restful-booker](https://restful-booker.herokuapp.com) | Public demo API for test practice | Access-control checks: writes must require a valid token |
| [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/) | Intentionally-vulnerable training app (run locally / in CI via Docker) | Reference target: proves a detector catches a real, known vulnerability |

This suite does **not** run against any system that is not on this list. It must never be pointed at production
systems, third-party sites, or any target without explicit authorization.

## What the checks do, and do not, do

- **Detection, not exploitation.** Payloads are detection-level only. There are no stacked statements
  (no `DROP`/`DELETE`/`UPDATE`), no time-based blind payloads, and no data-dumping `UNION` queries.
- **Non-destructive.** Checks do not create, alter or delete data on the shared demo targets (the booking
  access-control tests create a record, assert it cannot be changed without a token, and delete it afterwards).
- **Low volume.** The suite runs once per change and nightly, with a handful of payloads per check.

## Coverage (OWASP Top 10)

| Area | Check | OWASP |
|---|---|---|
| SQL injection | Login auth-bypass is blocked; no database error is leaked | A03 Injection |
| Cross-site scripting | Reflected input is HTML-encoded, not executable | A03 Injection |
| Broken access control | API write operations require a valid token | A01 Broken Access Control |
| Security misconfiguration | Recommended HTTP security headers are present | A05 Security Misconfiguration |

## How findings are handled

A failing negative check means a protection is missing: it is treated as a release-blocking finding by the
quality gate. Known, accepted gaps (for example the missing headers on ParaBank, DEF-005 and DEF-006) are
recorded in [DEFECTS.md](DEFECTS.md) and run as strict expected failures, so that remediation later turns the
check green and prompts a re-review.
