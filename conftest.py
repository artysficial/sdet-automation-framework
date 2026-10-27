"""Shared fixtures and hooks: browser lifecycle, failure evidence, tagging and known defects."""

import base64
import re
from pathlib import Path

import pytest

from framework.driver_factory import create_driver

REPORTS = Path(__file__).parent / "reports"
REPORT_TAGS = {"smoke", "regression", "negative", "contract", "auth", "catalog", "cart", "checkout",
               "banking", "security", "youtube", "injection", "xss", "authz", "reference_target", "known_defect"}

# Gherkin tags cannot carry arguments, so BDD scenarios tagged @known_defect map to their defect here
KNOWN_DEFECTS = {
    "test_sorting_works_for_the_problem_user_account":
        "DEF-001: product sorting has no effect for problem_user",
    "test_order_amounts_are_displayed_in_dollars_and_cents":
        "DEF-004: item total shows floating-point artefacts such as $59.980000000000004",
}


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="show the browser window instead of running headless")


def pytest_html_report_title(report):
    report.title = "SDET Automation Framework: detailed test report"


def pytest_collection_modifyitems(config, items):
    for item in items:
        nodeid = item.nodeid.replace("\\", "/")
        layer = "ui" if "tests/ui" in nodeid else "security" if "tests/security" in nodeid else "api"
        item.add_marker(getattr(pytest.mark, layer))
        # BDD scenarios tagged @known_defect reproduce a logged defect. strict=True turns an
        # unexpected pass into a failure, so a silent fix is noticed and the defect re-verified.
        if item.get_closest_marker("known_defect") and not item.get_closest_marker("xfail"):
            reason = KNOWN_DEFECTS.get(item.originalname, "Known defect, see docs/DEFECTS.md")
            item.add_marker(pytest.mark.xfail(reason=reason, strict=True))


@pytest.fixture(autouse=True)
def _record_tags(request, record_property):
    """Expose tags in the JUnit XML so the readiness report can group results."""
    tags = sorted({marker.name for marker in request.node.iter_markers()} & REPORT_TAGS)
    record_property("tags", ",".join(tags))


@pytest.fixture
def driver(request):
    browser = create_driver(headless=not request.config.getoption("--headed"))
    # pytest-bdd steps request this fixture dynamically, so keep a handle for the failure hook
    request.node.browser = browser
    yield browser
    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not (report.failed or hasattr(report, "wasxfail")):
        return
    browser = getattr(item, "browser", None)
    if browser is None:
        return

    png = browser.get_screenshot_as_png()
    path = REPORTS / "screenshots" / (re.sub(r"[^\w.-]+", "_", item.nodeid)[:150] + ".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html:
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.image(base64.b64encode(png).decode(), "Screenshot at failure"))
        extras.append(pytest_html.extras.url(browser.current_url, "Page URL"))
        report.extras = extras
