import os
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=None, help="Base URL of AUT")
    parser.addoption("--headed", action="store_true", help="Run browser headed (not headless)")

@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("--base-url") or os.environ.get("BASE_URL", "http://127.0.0.1:5010")

@pytest.fixture(scope="session")
def driver(pytestconfig):
    options = webdriver.ChromeOptions()
    if not pytestconfig.getoption("--headed"):
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,850")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield driver
    try:
        png = driver.get_screenshot_as_png()
        allure.attach(png, name="final_screenshot", attachment_type=allure.attachment_type.PNG)
    except Exception:
        pass
    driver.quit()
