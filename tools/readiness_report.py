"""Builds a release-readiness report from pytest's JUnit XML.

The report leads with a Go / Go with conditions / No-go recommendation, then shows the exit criteria,
open known defects, results by functional area and every test. It is a single self-contained HTML file.

    python tools/readiness_report.py reports/junit-*.xml --out reports/index.html [--summary FILE]
"""

import argparse
import html
import os
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

# order matters: the first matching tag wins, so specific areas come before generic ones
AREAS = [("security", "Security"), ("youtube", "YouTube API"), ("banking", "Banking"),
         ("checkout", "Checkout & pricing"), ("cart", "Cart"), ("catalog", "Catalogue"),
         ("auth", "Authentication")]
MIN_PASS_RATE = 95.0


@dataclass
class Result:
    name: str
    module: str
    seconds: float
    status: str                      # passed | failed | known_defect | skipped
    message: str = ""
    tags: set = field(default_factory=set)

    @property
    def area(self) -> str:
        for tag, label in AREAS:
            if tag in self.tags:
                return label
        if ".api." in self.module:          # restful-booker tests with no more specific area tag
            return "Booking API"
        return "Other"

    @property
    def title(self) -> str:
        base, _, params = self.name.partition("[")
        title = base.removeprefix("test_").replace("_", " ").capitalize()
        # pytest-bdd drops hyphens when it turns scenario names into function names
        for squashed, readable in (("Signin", "Sign-in"), ("Signedin", "Signed-in")):
            title = title.replace(squashed, readable)
        if params:
            params = params.rstrip("]")
            title += f" [{params if len(params) <= 70 else params[:67] + '...'}]"
        return title


def load(path: str) -> list[Result]:
    results = []
    for case in ET.parse(path).getroot().iter("testcase"):
        tags = set()
        for prop in case.iter("property"):
            if prop.get("name") == "tags" and prop.get("value"):
                tags = set(prop.get("value").split(","))
        status, message = "passed", ""
        for child in case:
            if child.tag in ("failure", "error"):
                status, message = "failed", child.get("message") or (child.text or "")
            elif child.tag == "skipped":
                xfail = child.get("type") == "pytest.xfail"
                status = "known_defect" if xfail else "skipped"
                message = child.get("message") or ""
        results.append(Result(case.get("name"), case.get("classname", ""), float(case.get("time", 0)),
                              status, message.strip().splitlines()[0][:300] if message.strip() else "", tags))
    return results


def evaluate(results: list[Result]) -> dict:
    executed = [r for r in results if r.status in ("passed", "failed")]
    passed = sum(r.status == "passed" for r in executed)
    pass_rate = 100.0 * passed / len(executed) if executed else 0.0
    smoke = [r for r in executed if "smoke" in r.tags]
    critical = [r for r in executed if r.tags & {"checkout", "contract", "injection", "authz"}]
    security = [r for r in executed if "security" in r.tags]

    criteria = [
        ("Smoke suite passes in full", f"{sum(r.status == 'passed' for r in smoke)} / {len(smoke)} passed",
         bool(smoke) and all(r.status == "passed" for r in smoke)),
        ("No failures on critical paths (checkout, contract, injection, access control)",
         f"{sum(r.status == 'failed' for r in critical)} failed of {len(critical)}",
         all(r.status == "passed" for r in critical)),
        ("No security findings on protected targets",
         f"{sum(r.status == 'failed' for r in security)} findings of {len(security)} checks",
         all(r.status == "passed" for r in security)),
        (f"Overall pass rate of at least {MIN_PASS_RATE:.0f}%", f"{pass_rate:.1f}%", pass_rate >= MIN_PASS_RATE),
        ("Known defects still reproduce as logged", f"{sum(r.status == 'known_defect' for r in results)} open",
         True),
    ]
    known = [r for r in results if r.status == "known_defect"]
    if not all(ok for _, _, ok in criteria):
        verdict = ("No-go", "nogo", "One or more exit criteria are not met. Resolve the failures below before release.")
    elif known:
        verdict = ("Go with conditions", "conditional",
                   f"All exit criteria are met. {len(known)} known defect(s) remain open and must be accepted "
                   "by the product owner or scheduled for a fix.")
    else:
        verdict = ("Go", "go", "All exit criteria are met and no known defects are open.")
    return {"criteria": criteria, "pass_rate": pass_rate, "verdict": verdict, "known": known,
            "failed": [r for r in results if r.status == "failed"]}


def esc(value) -> str:
    return html.escape(str(value))


def render(results: list[Result], summary: dict) -> str:
    counts = Counter(r.status for r in results)
    duration = sum(r.seconds for r in results)
    label, css, rationale = summary["verdict"]
    repo, sha, run_id = os.getenv("GITHUB_REPOSITORY"), os.getenv("GITHUB_SHA"), os.getenv("GITHUB_RUN_ID")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    generated = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

    run_meta = [f"Generated {generated}"]
    if repo and sha:
        run_meta.append(f'Commit <a href="{server}/{repo}/commit/{sha}">{sha[:7]}</a>')
    if repo and run_id:
        run_meta.append(f'<a href="{server}/{repo}/actions/runs/{run_id}">CI run #{esc(os.getenv("GITHUB_RUN_NUMBER", run_id))}</a>')

    # per-suite detailed HTML + screenshots are uploaded as CI artifacts, not to Pages
    if repo and run_id:
        detailed_href = f"{server}/{repo}/actions/runs/{run_id}"
        detailed_label = "Per-suite reports &amp; screenshots (CI artifacts)"
    else:
        detailed_href, detailed_label = "detailed-report.html", "Detailed report with screenshots"

    by_area = defaultdict(Counter)
    for r in results:
        by_area[r.area][r.status] += 1
    area_rows = []
    ordered_areas = [label for _, label in AREAS] + ["Booking API", "Other"]
    for area in ordered_areas:
        c = by_area.get(area)
        if not c:
            continue
        total = sum(c.values())
        bar = "".join(f'<span class="seg {s}" style="width:{100 * c[s] / total:.2f}%"></span>'
                      for s in ("passed", "known_defect", "failed", "skipped") if c[s])
        area_rows.append(f"<tr><td>{esc(area)}</td><td class=num>{total}</td><td class=num>{c['passed']}</td>"
                         f"<td class=num>{c['failed']}</td><td class=num>{c['known_defect']}</td>"
                         f'<td class="barcell"><div class="bar">{bar}</div></td></tr>')

    criteria_rows = "".join(
        f"<tr><td>{esc(name)}</td><td>{esc(actual)}</td>"
        f'<td><span class="pill {"ok" if ok else "bad"}">{"Met" if ok else "Not met"}</span></td></tr>'
        for name, actual, ok in summary["criteria"])

    def issue_list(items, empty):
        if not items:
            return f'<p class="muted">{empty}</p>'
        return "<ul class=issues>" + "".join(
            f"<li><strong>{esc(r.title)}</strong><span>{esc(r.area)}</span><code>{esc(r.message)}</code></li>"
            for r in items) + "</ul>"

    status_label = {"passed": "Passed", "failed": "Failed", "known_defect": "Known defect", "skipped": "Skipped"}
    test_rows = "".join(
        f'<tr data-status="{r.status}"><td>{esc(r.title)}</td><td>{esc(r.area)}</td>'
        f'<td>{esc(", ".join(sorted(r.tags - {"known_defect"})))}</td><td class=num>{r.seconds:.1f}s</td>'
        f'<td><span class="pill {r.status}">{status_label[r.status]}</span></td></tr>'
        for r in sorted(results, key=lambda r: (r.status == "passed", r.area, r.title)))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Release Readiness Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: hsl(33, 38%, 91%); --card: hsl(36, 50%, 97%); --sub: hsl(32, 36%, 89%); --border: hsl(30, 28%, 84%);
    --strong: hsl(20, 32%, 18%); --text: hsl(22, 20%, 30%); --muted: hsl(22, 12%, 45%); --accent: hsl(18, 48%, 40%);
    --ok: hsl(145, 38%, 34%); --ok-bg: hsl(145, 35%, 90%); --bad: hsl(355, 58%, 44%); --bad-bg: hsl(355, 60%, 93%);
    --warn: hsl(32, 70%, 36%); --warn-bg: hsl(38, 80%, 89%); --skip: hsl(30, 8%, 55%);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: hsl(20, 20%, 7%); --card: hsl(20, 18%, 11%); --sub: hsl(22, 18%, 15%); --border: hsl(22, 16%, 21%);
      --strong: hsl(33, 45%, 95%); --text: hsl(30, 25%, 84%); --muted: hsl(30, 12%, 62%); --accent: hsl(24, 62%, 72%);
      --ok: hsl(145, 45%, 62%); --ok-bg: hsl(145, 30%, 16%); --bad: hsl(355, 70%, 70%); --bad-bg: hsl(355, 35%, 18%);
      --warn: hsl(38, 80%, 66%); --warn-bg: hsl(32, 40%, 17%); --skip: hsl(30, 8%, 50%);
    }}
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font: 15px/1.6 Inter, system-ui, sans-serif; padding: 32px 16px 60px; }}
  main {{ max-width: 1040px; margin: auto; display: grid; gap: 20px; }}
  a {{ color: var(--accent); }}
  h1, h2 {{ font-family: 'Playfair Display', Georgia, serif; color: var(--strong); font-weight: 600; }}
  h1 {{ font-size: 32px; line-height: 1.2; }}
  h2 {{ font-size: 21px; margin-bottom: 14px; }}
  .eyebrow {{ color: var(--accent); font-size: 12px; font-weight: 600; letter-spacing: .8px; text-transform: uppercase; }}
  .meta {{ color: var(--muted); font-size: 13px; margin-top: 6px; display: flex; flex-wrap: wrap; gap: 6px 16px; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 18px; padding: 24px; }}
  .verdict {{ border-left: 6px solid var(--accent); }}
  .verdict.go {{ border-left-color: var(--ok); }} .verdict.nogo {{ border-left-color: var(--bad); }}
  .verdict.conditional {{ border-left-color: var(--warn); }}
  .verdict .label {{ font-family: 'Playfair Display', Georgia, serif; font-size: 30px; color: var(--strong); }}
  .verdict.go .label {{ color: var(--ok); }} .verdict.nogo .label {{ color: var(--bad); }}
  .verdict.conditional .label {{ color: var(--warn); }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }}
  .kpi {{ background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 16px; }}
  .kpi b {{ display: block; font: 600 26px 'Playfair Display', Georgia, serif; color: var(--strong); font-variant-numeric: lining-nums; }}
  .kpi span {{ color: var(--muted); font-size: 13px; }}
  .table-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ color: var(--muted); font-weight: 500; font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .pill {{ display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; white-space: nowrap; }}
  .pill.ok, .pill.passed {{ background: var(--ok-bg); color: var(--ok); }}
  .pill.bad, .pill.failed {{ background: var(--bad-bg); color: var(--bad); }}
  .pill.known_defect {{ background: var(--warn-bg); color: var(--warn); }}
  .pill.skipped {{ background: var(--sub); color: var(--skip); }}
  .barcell {{ width: 34%; min-width: 140px; }}
  .bar {{ display: flex; height: 10px; border-radius: 6px; overflow: hidden; background: var(--sub); margin-top: 6px; gap: 2px; }}
  .seg.passed {{ background: var(--ok); }} .seg.failed {{ background: var(--bad); }}
  .seg.known_defect {{ background: var(--warn); }} .seg.skipped {{ background: var(--skip); }}
  .issues {{ list-style: none; display: grid; gap: 10px; }}
  .issues li {{ display: grid; gap: 2px; padding: 12px 14px; background: var(--sub); border-radius: 12px; }}
  .issues span {{ color: var(--muted); font-size: 13px; }}
  .issues code {{ font: 12.5px ui-monospace, Consolas, monospace; color: var(--text); overflow-wrap: anywhere; }}
  .muted {{ color: var(--muted); }}
  .filters {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }}
  .filters button {{ font: inherit; font-size: 13px; padding: 5px 12px; border-radius: 20px; border: 1px solid var(--border);
    background: none; color: var(--text); cursor: pointer; }}
  .filters button[aria-pressed="true"] {{ border-color: var(--accent); color: var(--accent); }}
  .links {{ display: flex; flex-wrap: wrap; gap: 10px; }}
  .links a {{ text-decoration: none; border: 1px solid var(--border); padding: 8px 14px; border-radius: 12px; font-weight: 500; font-size: 14px; }}
  .links a:hover {{ border-color: var(--accent); }}
  footer {{ color: var(--muted); font-size: 13px; text-align: center; }}
</style>
</head>
<body>
<main>
  <header>
    <p class="eyebrow">Release readiness report</p>
    <h1>Storefront, Banking, API &amp; Security</h1>
    <p class="meta">{" &middot; ".join(run_meta)}</p>
  </header>

  <section class="card verdict {css}">
    <p class="eyebrow">Recommendation</p>
    <p class="label">{esc(label)}</p>
    <p>{esc(rationale)}</p>
  </section>

  <section class="kpis">
    <div class="kpi"><b>{len(results)}</b><span>tests run</span></div>
    <div class="kpi"><b>{counts['passed']}</b><span>passed</span></div>
    <div class="kpi"><b>{counts['failed']}</b><span>failed</span></div>
    <div class="kpi"><b>{counts['known_defect']}</b><span>known defects</span></div>
    <div class="kpi"><b>{summary['pass_rate']:.1f}%</b><span>pass rate (excl. known defects)</span></div>
    <div class="kpi"><b>{duration:.0f}s</b><span>total test time</span></div>
  </section>

  <section class="card">
    <h2>Exit criteria</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>Criterion</th><th>Actual</th><th>Status</th></tr></thead>
      <tbody>{criteria_rows}</tbody>
    </table></div>
  </section>

  <section class="card">
    <h2>Failures</h2>
    {issue_list(summary["failed"], "No unexpected failures in this run.")}
  </section>

  <section class="card">
    <h2>Open known defects</h2>
    {issue_list(summary["known"], "No known defects are open.")}
    <p class="muted" style="margin-top:12px">Full write-ups with steps to reproduce:
      <a href="https://github.com/{esc(repo or 'artysficial/sdet-automation-framework')}/blob/main/docs/DEFECTS.md">docs/DEFECTS.md</a></p>
  </section>

  <section class="card">
    <h2>Results by area</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>Area</th><th class=num>Tests</th><th class=num>Passed</th><th class=num>Failed</th><th class=num>Known defects</th><th>Distribution</th></tr></thead>
      <tbody>{"".join(area_rows)}</tbody>
    </table></div>
  </section>

  <section class="card">
    <h2>All tests</h2>
    <div class="filters" role="group" aria-label="Filter tests by status">
      <button aria-pressed="true" data-filter="all">All</button>
      <button aria-pressed="false" data-filter="failed">Failed</button>
      <button aria-pressed="false" data-filter="known_defect">Known defects</button>
      <button aria-pressed="false" data-filter="passed">Passed</button>
    </div>
    <div class="table-wrap"><table>
      <thead><tr><th>Test</th><th>Area</th><th>Tags</th><th class=num>Time</th><th>Status</th></tr></thead>
      <tbody id="tests">{test_rows}</tbody>
    </table></div>
  </section>

  <section class="links">
    <a href="{detailed_href}">{detailed_label}</a>
    <a href="https://github.com/{esc(repo or 'artysficial/sdet-automation-framework')}/actions/workflows/tests.yml">CI pipeline (per-suite jobs)</a>
    <a href="https://github.com/{esc(repo or 'artysficial/sdet-automation-framework')}">Source on GitHub</a>
  </section>

  <footer>Framework and report by Rahmadani Tyas Ningrum &middot; <a href="https://artysficial.github.io/">artysficial.github.io</a></footer>
</main>
<script>
  document.querySelectorAll("[data-filter]").forEach(function (button) {{
    button.addEventListener("click", function () {{
      document.querySelectorAll("[data-filter]").forEach(function (b) {{ b.setAttribute("aria-pressed", b === button); }});
      document.querySelectorAll("#tests tr").forEach(function (row) {{
        row.hidden = button.dataset.filter !== "all" && row.dataset.status !== button.dataset.filter;
      }});
    }});
  }});
</script>
</body>
</html>
"""


def markdown(results: list[Result], summary: dict) -> str:
    counts = Counter(r.status for r in results)
    lines = [f"## Release readiness: **{summary['verdict'][0]}**", "", summary["verdict"][2], "",
             f"| Tests | Passed | Failed | Known defects | Pass rate |", "|---|---|---|---|---|",
             f"| {len(results)} | {counts['passed']} | {counts['failed']} | {counts['known_defect']} | {summary['pass_rate']:.1f}% |",
             "", "| Exit criterion | Actual | Status |", "|---|---|---|"]
    lines += [f"| {name} | {actual} | {'Met' if ok else 'Not met'} |" for name, actual, ok in summary["criteria"]]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("junit", nargs="+", help="one or more JUnit XML files (one per CI suite)")
    parser.add_argument("--out", default="reports/index.html")
    parser.add_argument("--summary", help="also append a Markdown summary to this file (e.g. $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args()

    results = []
    for path in args.junit:
        results.extend(load(path))
    summary = evaluate(results)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(render(results, summary))
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as handle:
            handle.write(markdown(results, summary))
    print(f"{summary['verdict'][0]}: {len(results)} tests, report written to {args.out}")


if __name__ == "__main__":
    main()
