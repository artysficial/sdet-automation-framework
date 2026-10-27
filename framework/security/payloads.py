"""Non-destructive detection payloads and helpers for the security suite.

Scope: these are *detection-level* probes for authorized, intentionally-public test targets only.
They attempt to detect injection and XSS, not to exfiltrate or destroy data: there are no stacked
statements (no DROP/DELETE/UPDATE), no time-based blind payloads and no data-dumping UNIONs.
See docs/SECURITY_TESTING.md for the authorization boundary.
"""

import html
import re

# Classic authentication-bypass strings. A secure login must NOT grant access for any of these.
SQLI_AUTH_BYPASS = [
    "' OR '1'='1",
    "' OR '1'='1' -- ",
    "admin' -- ",
    '" OR "1"="1',
    "') OR ('1'='1",
]

# Probes that commonly trigger a database error if input reaches an unparameterised query.
# A well-built app must not echo a raw database error back to the client.
SQLI_ERROR_PROBES = ["'", "''", "' AND 1=CONVERT(int,'x')-- ", "')"]

# Reflected-XSS probes. If the value is reflected at all, it must come back HTML-encoded.
XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "\"><img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
]

# Signatures of a leaked database error, across common engines.
SQL_ERROR_SIGNATURES = re.compile(
    r"SQL syntax|SQLException|SQLSTATE|ORA-\d{5}|unclosed quotation|"
    r"quoted string not properly terminated|psql:|pg_query|"
    r"org\.hibernate|JDBC|syntax error at or near|Warning: mysqli?",
    re.IGNORECASE,
)


def leaks_sql_error(body: str) -> str | None:
    """Return the matched database-error signature if the response leaks one, else None."""
    match = SQL_ERROR_SIGNATURES.search(body or "")
    return match.group(0) if match else None


def is_reflected_unencoded(payload: str, body: str) -> bool:
    """True only if the raw payload appears in the body while its HTML-encoded form does not.

    Reflecting the encoded form (or not reflecting at all) is safe; reflecting the raw markup is the risk.
    """
    body = body or ""
    return payload in body and html.escape(payload, quote=True) not in body
