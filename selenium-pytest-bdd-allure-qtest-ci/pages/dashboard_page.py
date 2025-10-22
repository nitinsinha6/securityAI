import allure
from utils.waits import wait_for

class DashboardPage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip('/')

    @allure.step("Open dashboard with view='{view}'")
    def open(self, view="soc"):
        self.driver.get(f"{self.base_url}/?view={view}")
        return self

    @allure.step("Verify KPI tiles exist")
    def verify_kpis(self):
        wait_for(self.driver, ".kpi .v", by="css", timeout=15)
        return self

    @allure.step("Verify at least one chart image is shown")
    def verify_charts(self):
        wait_for(self.driver, "img", by="css", timeout=15)
        imgs = self.driver.find_elements("css selector", "img")
        assert any("static" in (i.get_attribute("src") or "") for i in imgs), "No chart images found"
        return self

    @allure.step("Verify top table has rows")
    def verify_table(self):
        wait_for(self.driver, "table[aria-label='top-insights']", by="css", timeout=15)
        rows = self.driver.find_elements("css selector", "table[aria-label='top-insights'] tbody tr")
        assert len(rows) > 0, "No rows found in top-insights table"
        return self
