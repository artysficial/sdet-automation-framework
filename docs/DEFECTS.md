# Defect log

Defects found by this suite in the two public demo applications under test. Each is reproduced automatically by a
test marked `known_defect`, which runs as a strict expected failure: if a defect is silently fixed, the test turns
red so it can be re-verified and closed.

| ID | Summary | Area | Severity | Priority | Status |
|---|---|---|---|---|---|
| [DEF-001](#def-001) | Product sorting has no effect for `problem_user` | Catalogue (UI) | Medium | P3 | Open |
| [DEF-002](#def-002) | Creating a booking with a missing required field returns 500 | Booking API | Medium | P2 | Open |
| [DEF-003](#def-003) | Invalid credentials return 200 instead of 401 | Booking API | Low | P3 | Open |
| [DEF-004](#def-004) | Item total shows floating-point artefacts at checkout | Checkout (UI) | High | P2 | Open |

Severity reflects impact on the user or integrator; priority reflects the recommended order of fixing.

---

## DEF-001

**Product sorting has no effect for `problem_user`**

| | |
|---|---|
| Environment | https://www.saucedemo.com, Chrome (headless and headed) |
| Test | `tests/ui/features/account_variants.feature`: *Sorting works for the problem_user account* |
| Severity / Priority | Medium / P3 |

**Steps to reproduce**
1. Sign in as `problem_user` / `secret_sauce`.
2. Select **Name (Z to A)** in the sort menu.

**Expected:** products are listed in reverse alphabetical order, as they are for `standard_user`.
**Actual:** the list order does not change.
**Impact:** shoppers on affected accounts cannot sort the catalogue; behaviour differs between account types.

---

## DEF-002

**Creating a booking with a missing required field returns 500 Internal Server Error**

| | |
|---|---|
| Environment | https://restful-booker.herokuapp.com |
| Test | `tests/api/test_booking_api.py::test_create_booking_missing_required_field_is_rejected_as_client_error` |
| Severity / Priority | Medium / P2 |

**Steps to reproduce**
```http
POST /booking
Content-Type: application/json
Accept: application/json

{"lastname": "QA", "totalprice": 150, "depositpaid": true,
 "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-04"}}
```

**Expected:** `400 Bad Request` with a message naming the missing `firstname` field.
**Actual:** `500 Internal Server Error`.
**Impact:** clients cannot tell a validation problem from a server fault; monitoring raises false server alerts and
retries are triggered for requests that can never succeed.

---

## DEF-003

**Invalid credentials return 200 OK instead of 401 Unauthorized**

| | |
|---|---|
| Environment | https://restful-booker.herokuapp.com |
| Test | `tests/api/test_booking_api.py::test_invalid_credentials_are_rejected_with_401` |
| Severity / Priority | Low / P3 |

**Steps to reproduce**
```http
POST /auth
Content-Type: application/json

{"username": "admin", "password": "not-the-password"}
```

**Expected:** `401 Unauthorized`.
**Actual:** `200 OK` with body `{"reason": "Bad credentials"}`. No token is issued, so this is not a security bypass.
**Impact:** integrations that rely on status codes treat a failed login as a success and only fail later.

---

## DEF-004

**Item total shows floating-point artefacts at checkout**

| | |
|---|---|
| Environment | https://www.saucedemo.com, Chrome |
| Test | `tests/ui/features/checkout.feature`: *Order amounts are displayed in dollars and cents* |
| Severity / Priority | High / P2 |

**Steps to reproduce**
1. Sign in as `standard_user`.
2. Add **Sauce Labs Fleece Jacket** ($49.99) and **Sauce Labs Bike Light** ($9.99) to the cart.
3. Check out with any name and postal code and continue to the overview.

**Expected:** `Item total: $59.98`.
**Actual:** `Item total: $59.980000000000004`. Tax ($4.80) and the grand total ($64.78) display correctly, so the
formatting is inconsistent within the same summary.
**Impact:** a customer-facing price is shown with binary floating-point noise, which undermines trust at the point of
payment. The arithmetic is correct to the cent (verified separately by the order-total scenarios), so the root cause
is display formatting: amounts should be rounded or held in integer cents before rendering.
