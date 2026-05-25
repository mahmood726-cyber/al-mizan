"""
Al-Mizan - Evidence Equipoise Monitor
Selenium test suite covering tabs, datasets, input modes, and SVG rendering.
Run: python test_al_mizan.py
"""

import os
import unittest

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "al-mizan.html")
URL = "file:///" + HTML_PATH.replace("\\", "/")
DATASET_ROW_COUNTS = {"exSteroids": 9, "exTXA": 7, "exGlucose": 7}


def get_driver():
    opts = Options()
    opts.page_load_strategy = "eager"
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,900")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    try:
        driver = webdriver.Chrome(options=opts)
    except WebDriverException as exc:
        raise unittest.SkipTest(f"Chrome WebDriver unavailable: {exc}") from exc
    driver.implicitly_wait(1)
    return driver


class AlMizanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.driver.get(URL)
        WebDriverWait(cls.driver, 5, poll_frequency=0.05).until(
            EC.presence_of_element_located((By.ID, "tab-input"))
        )

    @classmethod
    def tearDownClass(cls):
        logs = cls.driver.get_log("browser")
        severe = [entry for entry in logs if entry["level"] == "SEVERE" and "favicon" not in entry.get("message", "")]
        if severe:
            print(f"\nJS ERRORS ({len(severe)}):")
            for entry in severe:
                print(f"  {entry['message']}")
        cls.driver.quit()

    def _reload(self):
        self.driver.get(URL)
        self._wait(By.ID, "tab-input")

    def _wait(self, by, value, timeout=5):
        return WebDriverWait(self.driver, timeout, poll_frequency=0.05).until(
            EC.presence_of_element_located((by, value))
        )

    def _wait_for(self, predicate, timeout=5, message=""):
        return WebDriverWait(self.driver, timeout, poll_frequency=0.05).until(
            lambda driver: predicate(driver) or False,
            message,
        )

    def _click(self, by, value):
        element = self._wait(by, value)
        self.driver.execute_script("arguments[0].click()", element)
        return element

    def _row_count(self):
        return len(self.driver.find_elements(By.CSS_SELECTOR, "#studyTableBody tr"))

    def _wait_for_row_count(self, expected_rows, timeout=5):
        self._wait_for(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#studyTableBody tr")) == expected_rows, timeout)

    def _wait_for_active_panel(self, panel_id, timeout=5):
        self._wait_for(
            lambda driver: "active" in driver.find_element(By.ID, panel_id).get_attribute("class"),
            timeout,
        )

    def _wait_for_text(self, by, value, predicate, timeout=5):
        self._wait_for(lambda driver: predicate(driver.find_element(by, value).text), timeout)

    def _load_example(self, button_id):
        self._reload()
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="inputMode"][value="examples"]')
        self.driver.execute_script("arguments[0].click()", radio)
        self._wait_for(lambda driver: driver.find_element(By.ID, "examplesSection").is_displayed())
        self._click(By.ID, button_id)
        expected_rows = DATASET_ROW_COUNTS.get(button_id)
        if expected_rows is not None:
            self._wait_for_row_count(expected_rows)
        else:
            self._wait_for(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#studyTableBody tr")) > 0)

    def _run_analysis(self):
        self._click(By.ID, "runAnalysisBtn")
        self._wait_for(lambda driver: driver.find_element(By.ID, "balanceContent").value_of_css_property("display") != "none")
        self._wait_for_text(By.ID, "statRIS", lambda text: text != "--")

    def test_01_page_loads(self):
        self.assertIn("Al-Mizan", self.driver.title)

    def test_02_hero_visible(self):
        hero = self.driver.find_element(By.CSS_SELECTOR, ".hero-title")
        self.assertIn("Al-Mizan", hero.text)
        arabic = self.driver.find_element(By.CSS_SELECTOR, ".hero-title .arabic")
        self.assertTrue(arabic.text.strip())

    def test_03_four_tabs_exist(self):
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".tab-btn")
        self.assertEqual(len(tabs), 4)
        labels = [tab.text for tab in tabs]
        self.assertIn("1. Data Input", labels)
        self.assertIn("2. The Balance", labels)
        self.assertIn("3. The Waste", labels)
        self.assertIn("4. Report", labels)

    def test_04_initial_empty_state(self):
        self._reload()
        empty = self.driver.find_element(By.ID, "emptyTableMsg")
        self.assertTrue(empty.is_displayed())
        self.assertIn("No studies loaded", empty.text)

    def test_05_tab_click_navigation(self):
        self._click(By.ID, "tab-balance")
        self._wait_for_active_panel("panel-balance")
        self._click(By.ID, "tab-input")
        self._wait_for_active_panel("panel-input")

    def test_06_tab_keyboard_arrow(self):
        self._reload()
        tab = self.driver.find_element(By.ID, "tab-input")
        tab.send_keys(Keys.ARROW_RIGHT)
        self._wait_for(lambda driver: driver.find_element(By.ID, "tab-balance").get_attribute("aria-selected") == "true")

    def test_07_dark_mode_toggle(self):
        self._reload()
        button = self.driver.find_element(By.ID, "themeToggle")
        self.assertEqual(button.text, "Dark Mode")
        self.driver.execute_script("arguments[0].click()", button)
        self._wait_for(lambda driver: driver.find_element(By.TAG_NAME, "html").get_attribute("data-theme") == "dark")
        self.assertEqual(button.text, "Light Mode")
        self.driver.execute_script("arguments[0].click()", button)
        self._wait_for(lambda driver: driver.find_element(By.TAG_NAME, "html").get_attribute("data-theme") == "light")

    def test_08_input_mode_manual(self):
        self._reload()
        manual = self.driver.find_element(By.ID, "manualSection")
        csv = self.driver.find_element(By.ID, "csvSection")
        examples = self.driver.find_element(By.ID, "examplesSection")
        self.assertTrue(manual.is_displayed())
        self.assertFalse(csv.is_displayed())
        self.assertFalse(examples.is_displayed())

    def test_09_input_mode_csv(self):
        self._reload()
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="inputMode"][value="csv"]')
        self.driver.execute_script("arguments[0].click()", radio)
        self._wait_for(lambda driver: driver.find_element(By.ID, "csvSection").is_displayed())

    def test_10_input_mode_examples(self):
        self._reload()
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="inputMode"][value="examples"]')
        self.driver.execute_script("arguments[0].click()", radio)
        self._wait_for(lambda driver: driver.find_element(By.ID, "examplesSection").is_displayed())
        examples = self.driver.find_element(By.ID, "examplesSection")
        buttons = examples.find_elements(By.CSS_SELECTOR, ".example-btn")
        self.assertEqual(len(buttons), 4)

    def test_11_load_steroids(self):
        self._load_example("exSteroids")
        count_label = self.driver.find_element(By.ID, "studyCountLabel")
        self.assertIn("9", count_label.text)
        self.assertEqual(self._row_count(), 9)

    def test_12_steroids_analysis_red(self):
        self._load_example("exSteroids")
        self._run_analysis()
        verdict = self.driver.find_element(By.ID, "verdictLabel")
        self.assertEqual(verdict.text, "MIZAN-RED")

    def test_13_steroids_tipping_year(self):
        self._load_example("exSteroids")
        self._run_analysis()
        tipping = self.driver.find_element(By.ID, "statTipping")
        self.assertNotEqual(tipping.text, "--")
        self.assertTrue(tipping.text.isdigit())

    def test_14_steroids_waste_patients(self):
        self._load_example("exSteroids")
        self._run_analysis()
        self._click(By.ID, "tab-waste")
        self._wait_for_active_panel("panel-waste")
        waste_num = self.driver.find_element(By.ID, "wasteNumber")
        waste_n = int(waste_num.text.replace(",", ""))
        self.assertGreater(waste_n, 0)

    def test_15_steroids_tsa_svg(self):
        self._load_example("exSteroids")
        self._run_analysis()
        svg = self.driver.find_element(By.CSS_SELECTOR, "#tsaSvgContainer svg")
        circles = svg.find_elements(By.TAG_NAME, "circle")
        paths = svg.find_elements(By.TAG_NAME, "path")
        self.assertGreater(len(circles), 0)
        self.assertGreater(len(paths), 0)

    def test_16_steroids_forest_svg(self):
        self._load_example("exSteroids")
        self._run_analysis()
        svg = self.driver.find_element(By.CSS_SELECTOR, "#forestSvgContainer svg")
        paths = svg.find_elements(By.TAG_NAME, "path")
        self.assertGreaterEqual(len(paths), 9)

    def test_17_load_txa(self):
        self._load_example("exTXA")
        count_label = self.driver.find_element(By.ID, "studyCountLabel")
        self.assertIn("7", count_label.text)

    def test_18_txa_analysis_verdict(self):
        self._load_example("exTXA")
        self._run_analysis()
        verdict = self.driver.find_element(By.ID, "verdictLabel").text
        self.assertIn("MIZAN-", verdict)

    def test_19_load_glucose(self):
        self._load_example("exGlucose")
        count_label = self.driver.find_element(By.ID, "studyCountLabel")
        self.assertIn("7", count_label.text)

    def test_20_glucose_analysis_stats(self):
        self._load_example("exGlucose")
        self._run_analysis()
        for stat_id in ["statRIS", "statInfoFrac", "statPooled", "statI2", "statFragility"]:
            element = self.driver.find_element(By.ID, stat_id)
            self.assertNotEqual(element.text, "--", f"{stat_id} should have a value")

    def test_21_manual_add_study(self):
        self._reload()
        self.driver.find_element(By.ID, "studyName").send_keys("Test Study 2024")
        self.driver.find_element(By.ID, "studyYear").send_keys("2024")
        self.driver.find_element(By.ID, "effectSize").send_keys("0.85")
        self.driver.find_element(By.ID, "ciLower").send_keys("0.72")
        self.driver.find_element(By.ID, "ciUpper").send_keys("1.02")
        self.driver.find_element(By.ID, "nExp").send_keys("500")
        self.driver.find_element(By.ID, "nCtrl").send_keys("500")
        self._click(By.ID, "addStudyBtn")
        self._wait_for_row_count(1)
        count_label = self.driver.find_element(By.ID, "studyCountLabel")
        self.assertIn("1", count_label.text)

    def test_22_csv_parsing(self):
        self._reload()
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="inputMode"][value="csv"]')
        self.driver.execute_script("arguments[0].click()", radio)
        self._wait_for(lambda driver: driver.find_element(By.ID, "csvSection").is_displayed())
        csv_data = (
            "Study A, 2020, RR, 0.85, 0.72, 1.02, 500, 500\n"
            "Study B, 2021, RR, 0.78, 0.65, 0.94, 600, 600\n"
            "Study C, 2022, RR, 0.90, 0.80, 1.01, 400, 400"
        )
        textarea = self.driver.find_element(By.ID, "csvInput")
        textarea.send_keys(csv_data)
        self._click(By.ID, "parseCsvBtn")
        self._wait_for_row_count(3)

    def test_23_clear_data(self):
        self._load_example("exSteroids")
        self._click(By.ID, "clearDataBtn")
        self._wait_for_row_count(0)
        empty = self.driver.find_element(By.ID, "emptyTableMsg")
        self.assertTrue(empty.is_displayed())

    def test_24_delete_study_row(self):
        self._load_example("exSteroids")
        self.assertEqual(self._row_count(), 9)
        delete_button = self.driver.find_element(By.CSS_SELECTOR, '.delete-row-btn[data-idx="0"]')
        self.driver.execute_script("arguments[0].click()", delete_button)
        self._wait_for_row_count(8)

    def test_25_table_sort_by_year(self):
        self._load_example("exSteroids")
        year_header = self.driver.find_element(By.CSS_SELECTOR, 'th[data-sort="year"]')
        self.driver.execute_script("arguments[0].click()", year_header)
        first_year = self.driver.find_element(
            By.CSS_SELECTOR, '#studyTableBody tr:first-child input[data-field="year"]'
        ).get_attribute("value")
        self.driver.execute_script("arguments[0].click()", year_header)
        self._wait_for(
            lambda driver: driver.find_element(
                By.CSS_SELECTOR, '#studyTableBody tr:first-child input[data-field="year"]'
            ).get_attribute("value") != first_year
        )

    def test_26_report_summary_table(self):
        self._load_example("exSteroids")
        self._run_analysis()
        self._click(By.ID, "tab-report")
        self._wait_for(lambda driver: driver.find_element(By.ID, "reportContent").is_displayed())
        summary = self.driver.find_element(By.ID, "reportSummaryTable")
        rows = summary.find_elements(By.TAG_NAME, "tr")
        self.assertGreaterEqual(len(rows), 9)

    def test_27_report_methods_text(self):
        self._load_example("exSteroids")
        self._run_analysis()
        self._click(By.ID, "tab-report")
        self._wait_for(lambda driver: driver.find_element(By.ID, "methodsText").is_displayed())
        methods = self.driver.find_element(By.ID, "methodsText")
        self.assertIn("DerSimonian-Laird", methods.text)
        self.assertIn("O'Brien-Fleming", methods.text)

    def test_28_report_r_code(self):
        self._load_example("exSteroids")
        self._run_analysis()
        self._click(By.ID, "tab-report")
        self._wait_for(lambda driver: driver.find_element(By.ID, "rCodeBlock").is_displayed())
        r_code = self.driver.find_element(By.ID, "rCodeBlock")
        self.assertIn("library(meta)", r_code.text)
        self.assertIn("library(rpact)", r_code.text)
        self.assertIn("CRASH 2004", r_code.text)

    def test_29_settings_rerun(self):
        self._load_example("exSteroids")
        self._run_analysis()
        ris_before = self.driver.find_element(By.ID, "statRIS").text
        alpha_input = self.driver.find_element(By.ID, "settingAlpha")
        alpha_input.clear()
        alpha_input.send_keys("0.01")
        self._click(By.ID, "rerunBtn")
        self._wait_for(lambda driver: driver.find_element(By.ID, "statRIS").text != ris_before)

    def test_30_waste_chart_svg(self):
        self._load_example("exSteroids")
        self._run_analysis()
        self._click(By.ID, "tab-waste")
        self._wait_for_active_panel("panel-waste")
        svg = self.driver.find_element(By.CSS_SELECTOR, "#wasteSvgContainer svg")
        texts = svg.find_elements(By.TAG_NAME, "text")
        text_content = " ".join(text.text for text in texts)
        self.assertIn("Tipping", text_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
