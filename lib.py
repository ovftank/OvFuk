import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_code_2fa(key_2fa: str):
    url = f"https://2fa.live/tok/{key_2fa}"
    response = requests.get(url)
    data = response.json()
    token = data.get("token")
    return token


class AutoChrome:
    def __init__(self, enable_images: bool = False, enable_css: bool = True, headless: bool = False, proxy: str = ''):
        self.options = Options()
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument('--deny-permission-prompts')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument(
            "--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_experimental_option(
            "excludeSwitches", ['enable-automation'])
        self.options.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile': {
                'password_manager_enabled': False
            }
        })
        self.options.add_experimental_option(
            'excludeSwitches', ['disable-popup-blocking'])
        if headless:
            self.options.add_argument('--headless')
        if not enable_images:
            self.options.add_argument('--blink-settings=imagesEnabled=false')
            prefs = {"profile.managed_default_content_settings.images": 2}
            self.options.add_experimental_option("prefs", prefs)
        if not enable_css:
            self.options.add_experimental_option(
                "prefs", {"profile.managed_default_content_settings.stylesheets": 2})
            self.options.set_capability(
                'goog:loggingPrefs', {'browser': 'ALL'})
        if proxy:
            self.options.add_argument(f"--proxy-server={proxy}")
        self.driver = webdriver.Chrome(options=self.options)

    def login(self, username: str, password: str, key_2fa: str):
        cookie = {
            'name': 'locale',
            'value': 'en_GB'
        }
        self.driver.get('https://mbasic.facebook.com')
        self.driver.add_cookie(cookie)
        username_input = self.driver.find_element(By.ID, 'm_login_email')
        username_input.clear()
        username_input.send_keys(username)
        password_input = self.driver.find_element(By.NAME, 'pass')
        password_input.clear()
        password_input.send_keys(password)
        login_button = self.driver.find_element(By.NAME, 'login')
        login_button.click()
        if 'https://mbasic.facebook.com/login/' in self.driver.current_url:
            return "FAILED"
        if 'https://mbasic.facebook.com/checkpoint/?_rdr' in self.driver.current_url:
            code_2fa = get_code_2fa(key_2fa)
            code_2fa_input = self.driver.find_element(
                By.NAME, 'approvals_code')
            code_2fa_input.clear()
            code_2fa_input.send_keys(code_2fa)
            submit_button = self.driver.find_element(
                By.NAME, 'submit[Submit Code]')
            submit_button.click()
            if 'https://mbasic.facebook.com/login/checkpoint/' in self.driver.current_url:
                for i in range(10):
                    if i == 9:
                        return "FAILED"
                    time.sleep(1)
                    submit_button = self.driver.find_element(
                        By.NAME, 'submit[Continue]')
                    submit_button.click()
                    if 'https://mbasic.facebook.com/login/checkpoint/' not in self.driver.current_url:
                        break
        time.sleep(10)
