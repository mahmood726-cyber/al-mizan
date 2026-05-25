"""Al-Mizan integration tests — evidence equipoise monitor."""

import sys

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, __import__("os").path.dirname(__file__))
from conftest import wait_for_app_ready, wait_for_rows, wait_for_text


@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)
    wait_for_app_ready(driver)


class TestAppLoads:
    def test_title(self, driver):
        assert "Al-Mizan" in driver.title

    def test_no_js_errors(self, driver):
        logs = driver.get_log("browser")
        severe = [entry for entry in logs if entry["level"] == "SEVERE"]
        assert len(severe) == 0, f"JS errors: {severe}"

    def test_tabs_present(self, driver):
        tabs = driver.find_elements("css selector", ".tab-btn")
        assert len(tabs) >= 4


class TestTabSwitching:
    def test_switch_to_balance(self, driver):
        driver.find_element("id", "tab-balance").click()
        panel = driver.find_element("id", "panel-balance")
        assert panel.is_displayed()

    def test_switch_back_to_input(self, driver):
        driver.find_element("id", "tab-input").click()
        panel = driver.find_element("id", "panel-input")
        assert panel.is_displayed()


class TestExampleData:
    def test_load_steroids(self, driver):
        driver.find_element("id", "tab-input").click()
        radio = driver.find_element("css selector", 'input[name="inputMode"][value="examples"]')
        driver.execute_script("arguments[0].click()", radio)
        WebDriverWait(driver, 5, poll_frequency=0.05).until(
            lambda d: d.find_element(By.ID, "examplesSection").is_displayed()
        )
        driver.execute_script("document.getElementById('exSteroids').click()")
        wait_for_rows(driver, 9)

    def test_run_analysis(self, driver):
        rows = driver.find_elements("css selector", "#studyTableBody tr")
        if len(rows) < 2:
            radio = driver.find_element("css selector", 'input[name="inputMode"][value="examples"]')
            driver.execute_script("arguments[0].click()", radio)
            WebDriverWait(driver, 5, poll_frequency=0.05).until(
                lambda d: d.find_element(By.ID, "examplesSection").is_displayed()
            )
            driver.execute_script("document.getElementById('exSteroids') && document.getElementById('exSteroids').click()")
            wait_for_rows(driver, 9)
        btn = driver.find_element("id", "runAnalysisBtn")
        driver.execute_script("arguments[0].click()", btn)
        wait_for_text(driver, By.ID, "statRIS", lambda text: text != "--")
        driver.find_element("id", "tab-balance").click()
        WebDriverWait(driver, 5, poll_frequency=0.05).until(
            lambda d: d.find_element(By.ID, "panel-balance").is_displayed()
        )
        panel = driver.find_element("id", "panel-balance")
        assert panel.is_displayed(), "Balance panel should be visible"


class TestDarkMode:
    def test_toggle_theme(self, driver):
        toggle = driver.find_element("id", "themeToggle")
        initial_theme = driver.find_element("tag name", "html").get_attribute("data-theme")
        toggle.click()
        WebDriverWait(driver, 5, poll_frequency=0.05).until(
            lambda d: d.find_element(By.TAG_NAME, "html").get_attribute("data-theme") != initial_theme
        )
        theme = driver.find_element("tag name", "html").get_attribute("data-theme")
        assert theme in ("dark", "light")
        toggle.click()
        WebDriverWait(driver, 5, poll_frequency=0.05).until(
            lambda d: d.find_element(By.TAG_NAME, "html").get_attribute("data-theme") == initial_theme
        )


class TestReport:
    def test_report_tab_exists(self, driver):
        driver.find_element("id", "tab-report").click()
        WebDriverWait(driver, 5, poll_frequency=0.05).until(
            lambda d: d.find_element(By.ID, "panel-report").is_displayed()
        )
        panel = driver.find_element("id", "panel-report")
        assert panel.is_displayed()
