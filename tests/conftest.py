import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(report, config):
    if report.when == "call" and report.passed:
        if "test_epic_" in report.nodeid:
            return (
                "passed",
                ".",
                ("PASSED [EPIC]", {"green": True, "bold": True}),
            )


def pytest_collection_modifyitems(items):
    for item in items:
        if "test_epic_" in item.nodeid:
            item._nodeid = f"\033[1;92m{item.nodeid}\033[0m"