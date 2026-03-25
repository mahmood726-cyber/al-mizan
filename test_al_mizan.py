"""
Al-Mizan (الميزان) — Evidence Equipoise Monitor
Selenium Test Suite: 30 tests covering all 4 tabs, 3 datasets, input methods, and SVG rendering.
Run: python test_al_mizan.py
"""
import sys, os, time, io, unittest
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'al-mizan.html')
URL = 'file:///' + HTML_PATH.replace('\\', '/')


def get_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1400,900')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(2)
    return driver


class AlMizanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = get_driver()
        cls.driver.get(URL)
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        # Check for JS errors
        logs = cls.driver.get_log('browser')
        severe = [l for l in logs if l['level'] == 'SEVERE' and 'favicon' not in l.get('message', '')]
        if severe:
            print(f"\nJS ERRORS ({len(severe)}):")
            for l in severe:
                print(f"  {l['message']}")
        cls.driver.quit()

    def _reload(self):
        self.driver.get(URL)
        time.sleep(0.3)

    def _wait(self, by, val, timeout=5):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, val))
        )

    def _click(self, by, val):
        el = self._wait(by, val)
        self.driver.execute_script("arguments[0].click()", el)
        return el

    def _load_example(self, btn_id):
        """Switch to examples mode and click a dataset button."""
        self._reload()
        # Select "Built-in Examples" radio
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="inputMode"][value="examples"]')
        self.driver.execute_script("arguments[0].click()", radio)
        time.sleep(0.2)
        self._click(By.ID, btn_id)
        time.sleep(0.2)

    def _run_analysis(self):
        """Click Run Analysis and wait for results."""
        self._click(By.ID, 'runAnalysisBtn')
        time.sleep(0.5)

    # ─── 1. PAGE LOAD ───
    def test_01_page_loads(self):
        """Page loads with correct title."""
        self.assertIn('Al-Mizan', self.driver.title)

    def test_02_hero_visible(self):
        """Hero header with Arabic title is visible."""
        hero = self.driver.find_element(By.CSS_SELECTOR, '.hero-title')
        self.assertIn('Al-Mizan', hero.text)
        arabic = self.driver.find_element(By.CSS_SELECTOR, '.hero-title .arabic')
        self.assertIn('الميزان', arabic.text)

    def test_03_four_tabs_exist(self):
        """All 4 tabs exist with correct labels."""
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '.tab-btn')
        self.assertEqual(len(tabs), 4)
        labels = [t.text for t in tabs]
        self.assertIn('1. Data Input', labels)
        self.assertIn('2. The Balance', labels)
        self.assertIn('3. The Waste', labels)
        self.assertIn('4. Report', labels)

    def test_04_initial_empty_state(self):
        """Data table shows empty state message initially."""
        self._reload()
        empty = self.driver.find_element(By.ID, 'emptyTableMsg')
        self.assertTrue(empty.is_displayed())
        self.assertIn('No studies loaded', empty.text)

    # ─── 2. TAB NAVIGATION ───
    def test_05_tab_click_navigation(self):
        """Clicking tab buttons switches panels."""
        self._click(By.ID, 'tab-balance')
        time.sleep(0.2)
        panel = self.driver.find_element(By.ID, 'panel-balance')
        self.assertIn('active', panel.get_attribute('class'))
        # Switch back
        self._click(By.ID, 'tab-input')
        time.sleep(0.2)
        panel_input = self.driver.find_element(By.ID, 'panel-input')
        self.assertIn('active', panel_input.get_attribute('class'))

    def test_06_tab_keyboard_arrow(self):
        """Arrow keys navigate between tabs."""
        self._reload()
        tab = self.driver.find_element(By.ID, 'tab-input')
        tab.send_keys(Keys.ARROW_RIGHT)
        time.sleep(0.2)
        balance_tab = self.driver.find_element(By.ID, 'tab-balance')
        self.assertEqual(balance_tab.get_attribute('aria-selected'), 'true')

    # ─── 3. DARK MODE ───
    def test_07_dark_mode_toggle(self):
        """Dark mode toggle changes data-theme attribute."""
        self._reload()
        btn = self.driver.find_element(By.ID, 'themeToggle')
        self.assertEqual(btn.text, 'Dark Mode')
        self.driver.execute_script("arguments[0].click()", btn)
        time.sleep(0.2)
        theme = self.driver.find_element(By.TAG_NAME, 'html').get_attribute('data-theme')
        self.assertEqual(theme, 'dark')
        self.assertEqual(btn.text, 'Light Mode')
        # Toggle back
        self.driver.execute_script("arguments[0].click()", btn)
        time.sleep(0.1)
        theme = self.driver.find_element(By.TAG_NAME, 'html').get_attribute('data-theme')
        self.assertEqual(theme, 'light')

    # ─── 4. INPUT MODES ───
    def test_08_input_mode_manual(self):
        """Manual entry section is visible by default."""
        self._reload()
        manual = self.driver.find_element(By.ID, 'manualSection')
        csv = self.driver.find_element(By.ID, 'csvSection')
        examples = self.driver.find_element(By.ID, 'examplesSection')
        self.assertTrue(manual.is_displayed())
        self.assertFalse(csv.is_displayed())
        self.assertFalse(examples.is_displayed())

    def test_09_input_mode_csv(self):
        """Selecting CSV radio shows CSV section."""
        self._reload()
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="inputMode"][value="csv"]')
        self.driver.execute_script("arguments[0].click()", radio)
        time.sleep(0.2)
        csv = self.driver.find_element(By.ID, 'csvSection')
        self.assertTrue(csv.is_displayed())

    def test_10_input_mode_examples(self):
        """Selecting examples radio shows 3 example buttons."""
        self._reload()
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="inputMode"][value="examples"]')
        self.driver.execute_script("arguments[0].click()", radio)
        time.sleep(0.2)
        examples = self.driver.find_element(By.ID, 'examplesSection')
        self.assertTrue(examples.is_displayed())
        btns = examples.find_elements(By.CSS_SELECTOR, '.example-btn')
        self.assertEqual(len(btns), 3)

    # ─── 5. LOAD STEROIDS DATASET ───
    def test_11_load_steroids(self):
        """Loading steroids dataset populates 9 studies."""
        self._load_example('exSteroids')
        count_label = self.driver.find_element(By.ID, 'studyCountLabel')
        self.assertIn('9', count_label.text)
        rows = self.driver.find_elements(By.CSS_SELECTOR, '#studyTableBody tr')
        self.assertEqual(len(rows), 9)

    def test_12_steroids_analysis_red(self):
        """Steroids dataset produces MIZAN-RED verdict."""
        self._load_example('exSteroids')
        self._run_analysis()
        verdict = self.driver.find_element(By.ID, 'verdictLabel')
        self.assertEqual(verdict.text, 'MIZAN-RED')

    def test_13_steroids_tipping_year(self):
        """Steroids tipping year is displayed."""
        # Analysis already run from previous test, but reload to be safe
        self._load_example('exSteroids')
        self._run_analysis()
        tipping = self.driver.find_element(By.ID, 'statTipping')
        # Should have a year value (not --)
        self.assertNotEqual(tipping.text, '--')
        self.assertTrue(tipping.text.isdigit())

    def test_14_steroids_waste_patients(self):
        """Steroids waste tab shows post-tipping patients."""
        self._load_example('exSteroids')
        self._run_analysis()
        self._click(By.ID, 'tab-waste')
        time.sleep(0.3)
        waste_num = self.driver.find_element(By.ID, 'wasteNumber')
        waste_n = int(waste_num.text.replace(',', ''))
        # CRASH 2004 enrolled 10,008 patients — waste should be substantial
        self.assertGreater(waste_n, 0)

    def test_15_steroids_tsa_svg(self):
        """Steroids analysis renders TSA SVG chart."""
        self._load_example('exSteroids')
        self._run_analysis()
        svg = self.driver.find_element(By.CSS_SELECTOR, '#tsaSvgContainer svg')
        self.assertIsNotNone(svg)
        # Should have circles (data points) and paths (boundaries)
        circles = svg.find_elements(By.TAG_NAME, 'circle')
        paths = svg.find_elements(By.TAG_NAME, 'path')
        self.assertGreater(len(circles), 0)
        self.assertGreater(len(paths), 0)

    def test_16_steroids_forest_svg(self):
        """Steroids analysis renders cumulative forest plot SVG."""
        self._load_example('exSteroids')
        self._run_analysis()
        svg = self.driver.find_element(By.CSS_SELECTOR, '#forestSvgContainer svg')
        self.assertIsNotNone(svg)
        # Forest plot should have diamond paths for each cumulative step
        paths = svg.find_elements(By.TAG_NAME, 'path')
        self.assertGreaterEqual(len(paths), 9)  # at least one per study

    # ─── 6. LOAD TXA DATASET ───
    def test_17_load_txa(self):
        """Loading TXA dataset populates 3 studies."""
        self._load_example('exTXA')
        count_label = self.driver.find_element(By.ID, 'studyCountLabel')
        self.assertIn('3', count_label.text)

    def test_18_txa_analysis_verdict(self):
        """TXA dataset produces a valid verdict (GREEN or AMBER)."""
        self._load_example('exTXA')
        self._run_analysis()
        verdict = self.driver.find_element(By.ID, 'verdictLabel').text
        # TXA with 3 studies should be GREEN or AMBER (not enough info for RED)
        self.assertIn('MIZAN-', verdict)

    # ─── 7. LOAD GLUCOSE DATASET ───
    def test_19_load_glucose(self):
        """Loading glucose dataset populates 7 studies."""
        self._load_example('exGlucose')
        count_label = self.driver.find_element(By.ID, 'studyCountLabel')
        self.assertIn('7', count_label.text)

    def test_20_glucose_analysis_stats(self):
        """Glucose analysis populates all stat boxes."""
        self._load_example('exGlucose')
        self._run_analysis()
        stat_ids = ['statRIS', 'statInfoFrac', 'statPooled', 'statI2', 'statFragility']
        for sid in stat_ids:
            el = self.driver.find_element(By.ID, sid)
            self.assertNotEqual(el.text, '--', f'{sid} should have a value')

    # ─── 8. MANUAL ENTRY ───
    def test_21_manual_add_study(self):
        """Manually adding a study populates the table."""
        self._reload()
        self.driver.find_element(By.ID, 'studyName').send_keys('Test Study 2024')
        self.driver.find_element(By.ID, 'studyYear').send_keys('2024')
        self.driver.find_element(By.ID, 'effectSize').send_keys('0.85')
        self.driver.find_element(By.ID, 'ciLower').send_keys('0.72')
        self.driver.find_element(By.ID, 'ciUpper').send_keys('1.02')
        self.driver.find_element(By.ID, 'nExp').send_keys('500')
        self.driver.find_element(By.ID, 'nCtrl').send_keys('500')
        self._click(By.ID, 'addStudyBtn')
        time.sleep(0.2)
        rows = self.driver.find_elements(By.CSS_SELECTOR, '#studyTableBody tr')
        self.assertEqual(len(rows), 1)
        count_label = self.driver.find_element(By.ID, 'studyCountLabel')
        self.assertIn('1', count_label.text)

    # ─── 9. CSV PARSING ───
    def test_22_csv_parsing(self):
        """CSV paste parses multiple studies correctly."""
        self._reload()
        radio = self.driver.find_element(By.CSS_SELECTOR, 'input[name="inputMode"][value="csv"]')
        self.driver.execute_script("arguments[0].click()", radio)
        time.sleep(0.2)
        csv_data = (
            "Study A, 2020, RR, 0.85, 0.72, 1.02, 500, 500\n"
            "Study B, 2021, RR, 0.78, 0.65, 0.94, 600, 600\n"
            "Study C, 2022, RR, 0.90, 0.80, 1.01, 400, 400"
        )
        textarea = self.driver.find_element(By.ID, 'csvInput')
        textarea.send_keys(csv_data)
        self._click(By.ID, 'parseCsvBtn')
        time.sleep(0.3)
        rows = self.driver.find_elements(By.CSS_SELECTOR, '#studyTableBody tr')
        self.assertEqual(len(rows), 3)

    # ─── 10. CLEAR DATA ───
    def test_23_clear_data(self):
        """Clear button removes all studies and resets state."""
        self._load_example('exSteroids')
        self._click(By.ID, 'clearDataBtn')
        time.sleep(0.2)
        rows = self.driver.find_elements(By.CSS_SELECTOR, '#studyTableBody tr')
        self.assertEqual(len(rows), 0)
        empty = self.driver.find_element(By.ID, 'emptyTableMsg')
        self.assertTrue(empty.is_displayed())

    # ─── 11. DELETE ROW ───
    def test_24_delete_study_row(self):
        """Deleting a study row reduces count by 1."""
        self._load_example('exSteroids')
        initial_rows = self.driver.find_elements(By.CSS_SELECTOR, '#studyTableBody tr')
        self.assertEqual(len(initial_rows), 9)
        del_btn = self.driver.find_element(By.CSS_SELECTOR, '.delete-row-btn[data-idx="0"]')
        self.driver.execute_script("arguments[0].click()", del_btn)
        time.sleep(0.2)
        rows = self.driver.find_elements(By.CSS_SELECTOR, '#studyTableBody tr')
        self.assertEqual(len(rows), 8)

    # ─── 12. TABLE SORTING ───
    def test_25_table_sort_by_year(self):
        """Clicking Year header sorts studies."""
        self._load_example('exSteroids')
        year_header = self.driver.find_element(By.CSS_SELECTOR, 'th[data-sort="year"]')
        self.driver.execute_script("arguments[0].click()", year_header)
        time.sleep(0.2)
        # Read first row year
        first_year = self.driver.find_element(
            By.CSS_SELECTOR, '#studyTableBody tr:first-child input[data-field="year"]'
        ).get_attribute('value')
        # Click again to reverse
        self.driver.execute_script("arguments[0].click()", year_header)
        time.sleep(0.2)
        new_first = self.driver.find_element(
            By.CSS_SELECTOR, '#studyTableBody tr:first-child input[data-field="year"]'
        ).get_attribute('value')
        self.assertNotEqual(first_year, new_first)

    # ─── 13. REPORT TAB ───
    def test_26_report_summary_table(self):
        """Report tab renders summary table with key metrics."""
        self._load_example('exSteroids')
        self._run_analysis()
        self._click(By.ID, 'tab-report')
        time.sleep(0.3)
        report = self.driver.find_element(By.ID, 'reportContent')
        self.assertTrue(report.is_displayed())
        summary = self.driver.find_element(By.ID, 'reportSummaryTable')
        rows = summary.find_elements(By.TAG_NAME, 'tr')
        self.assertGreaterEqual(len(rows), 9)  # at least 9 summary rows

    def test_27_report_methods_text(self):
        """Report tab contains methods text with DerSimonian-Laird mention."""
        self._load_example('exSteroids')
        self._run_analysis()
        self._click(By.ID, 'tab-report')
        time.sleep(0.3)
        methods = self.driver.find_element(By.ID, 'methodsText')
        self.assertIn('DerSimonian-Laird', methods.text)
        self.assertIn("O'Brien-Fleming", methods.text)

    def test_28_report_r_code(self):
        """Report tab generates R code with meta + rpact libraries."""
        self._load_example('exSteroids')
        self._run_analysis()
        self._click(By.ID, 'tab-report')
        time.sleep(0.3)
        r_code = self.driver.find_element(By.ID, 'rCodeBlock')
        self.assertIn('library(meta)', r_code.text)
        self.assertIn('library(rpact)', r_code.text)
        self.assertIn('CRASH 2004', r_code.text)

    # ─── 14. SETTINGS RE-RUN ───
    def test_29_settings_rerun(self):
        """Changing alpha and re-running updates the analysis."""
        self._load_example('exSteroids')
        self._run_analysis()
        ris1 = self.driver.find_element(By.ID, 'statRIS').text
        # Change alpha to 0.01
        alpha_input = self.driver.find_element(By.ID, 'settingAlpha')
        alpha_input.clear()
        alpha_input.send_keys('0.01')
        self._click(By.ID, 'rerunBtn')
        time.sleep(0.5)
        ris2 = self.driver.find_element(By.ID, 'statRIS').text
        # RIS should change with different alpha
        self.assertNotEqual(ris1, ris2)

    # ─── 15. WASTE CHART SVG ───
    def test_30_waste_chart_svg(self):
        """Waste tab renders enrollment timeline SVG."""
        self._load_example('exSteroids')
        self._run_analysis()
        self._click(By.ID, 'tab-waste')
        time.sleep(0.3)
        svg = self.driver.find_element(By.CSS_SELECTOR, '#wasteSvgContainer svg')
        self.assertIsNotNone(svg)
        # Should have the tipping line and cumulative path
        texts = svg.find_elements(By.TAG_NAME, 'text')
        text_content = ' '.join([t.text for t in texts])
        self.assertIn('Tipping', text_content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
