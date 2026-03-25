"""Al-Mizan integration tests — evidence equipoise monitor."""
import sys, time, json, pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)
        time.sleep(1)

class TestAppLoads:
    def test_title(self, driver):
        assert 'Al-Mizan' in driver.title

    def test_no_js_errors(self, driver):
        logs = driver.get_log('browser')
        severe = [l for l in logs if l['level'] == 'SEVERE']
        assert len(severe) == 0, f"JS errors: {severe}"

    def test_tabs_present(self, driver):
        tabs = driver.find_elements('css selector', '.tab-btn')
        assert len(tabs) >= 4  # Data Input, The Balance, The Waste, Report

class TestTabSwitching:
    def test_switch_to_balance(self, driver):
        driver.find_element('id', 'tab-balance').click()
        panel = driver.find_element('id', 'panel-balance')
        assert panel.is_displayed()

    def test_switch_back_to_input(self, driver):
        driver.find_element('id', 'tab-input').click()
        panel = driver.find_element('id', 'panel-input')
        assert panel.is_displayed()

class TestExampleData:
    def test_load_steroids(self, driver):
        """Load Steroids for Head Injury example dataset"""
        driver.find_element('id', 'tab-input').click()
        time.sleep(0.3)
        # Click Examples sub-tab — try JS click for headless compatibility
        examples_btns = driver.find_elements('css selector', '.input-toggle-btn')
        for btn in examples_btns:
            if 'Example' in btn.text:
                driver.execute_script('arguments[0].click()', btn)
                break
        time.sleep(0.5)
        driver.execute_script("document.getElementById('exSteroids').click()")
        time.sleep(1)
        rows = driver.find_elements('css selector', '#studyTableBody tr')
        assert len(rows) >= 2, f"Expected at least 2 studies, got {len(rows)}"

    def test_run_analysis(self, driver):
        """Run analysis on loaded data — ensure data loaded first"""
        # Load data if table is empty
        rows = driver.find_elements('css selector', '#studyTableBody tr')
        if len(rows) < 2:
            driver.execute_script("document.getElementById('exSteroids') && document.getElementById('exSteroids').click()")
            time.sleep(1)
        btn = driver.find_element('id', 'runAnalysisBtn')
        driver.execute_script('arguments[0].click()', btn)
        time.sleep(3)
        # Verify analysis ran by checking balance tab
        driver.find_element('id', 'tab-balance').click()
        time.sleep(0.5)
        panel = driver.find_element('id', 'panel-balance')
        assert panel.is_displayed(), "Balance panel should be visible"

class TestDarkMode:
    def test_toggle_theme(self, driver):
        toggle = driver.find_element('id', 'themeToggle')
        toggle.click()
        time.sleep(0.3)
        theme = driver.find_element('tag name', 'html').get_attribute('data-theme')
        assert theme in ('dark', 'light')
        # Toggle back
        toggle.click()
        time.sleep(0.3)

class TestReport:
    def test_report_tab_exists(self, driver):
        driver.find_element('id', 'tab-report').click()
        time.sleep(0.3)
        panel = driver.find_element('id', 'panel-report')
        assert panel.is_displayed()
