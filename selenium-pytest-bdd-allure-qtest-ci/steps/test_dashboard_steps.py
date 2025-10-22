import socket, allure, pytest
from urllib.parse import urlparse
from pytest_bdd import scenarios, given, when, then, parsers
from pages.dashboard_page import DashboardPage

scenarios("../features/dashboard.feature")

def _is_port_open(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

@given("the app is running")
def app_running(base_url):
    u = urlparse(base_url)
    host = u.hostname or "127.0.0.1"
    port = u.port or 5010
    if not _is_port_open(host, port, timeout=2.0):
        pytest.skip(f"App not reachable at {base_url}; start the server first")

@when(parsers.parse('I open the "{view}" dashboard'))
def open_dashboard(driver, base_url, view):
    page = DashboardPage(driver, base_url).open(view=view)
    allure.dynamic.label("tms", f"RBC-SEC-DASH-{view.upper()}")
    return page

@then("I see KPI tiles")
def see_kpis(driver, base_url):
    DashboardPage(driver, base_url).verify_kpis()

@then("I see charts")
def see_charts(driver, base_url):
    DashboardPage(driver, base_url).verify_charts()

@then("I see a populated top insights table")
def see_table(driver, base_url):
    DashboardPage(driver, base_url).verify_table()
