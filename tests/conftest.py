"""Shared Selenium fixtures for Al-Mizan tests."""
import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

HTML = os.path.join(os.path.dirname(__file__), '..', 'al-mizan.html')

@pytest.fixture(scope='session')
def driver():
    opts = Options()
    opts.page_load_strategy = 'eager'
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    try:
        d = webdriver.Chrome(options=opts)
    except WebDriverException as exc:
        pytest.skip(f"Chrome WebDriver unavailable: {exc}")
    d.implicitly_wait(1)
    yield d
    d.quit()

@pytest.fixture(scope='session')
def app_url():
    return 'file:///' + os.path.abspath(HTML).replace('\\', '/')


def js(driver, script):
    return driver.execute_script('return ' + script)


def wait_for_app_ready(driver, timeout=5):
    WebDriverWait(driver, timeout, poll_frequency=0.05).until(
        lambda d: d.find_element(By.ID, 'tab-input').is_displayed()
    )


def wait_for_rows(driver, expected_rows, timeout=5):
    WebDriverWait(driver, timeout, poll_frequency=0.05).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, '#studyTableBody tr')) == expected_rows
    )


def wait_for_text(driver, by, value, predicate, timeout=5):
    WebDriverWait(driver, timeout, poll_frequency=0.05).until(
        lambda d: predicate(d.find_element(by, value).text)
    )
