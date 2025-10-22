from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BY = {
    "id": By.ID,
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "name": By.NAME,
    "link": By.LINK_TEXT,
}

def wait_for(driver, locator: str, by: str = "css", timeout: int = 15):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((BY[by], locator)))
