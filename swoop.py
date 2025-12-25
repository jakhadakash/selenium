import pytest
import time
from selenium.common.exceptions import TimeoutException
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class TestSuperloop():

    def setup_method(self, method):
        # ================= Load JSON Test Data =================
        data_file = os.path.join(os.path.dirname(__file__), "test_data3.json")
        with open(data_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        # ================= Chrome Setup =================
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Position window on right half of screen
        screen_width = self.driver.execute_script("return window.screen.width;")
        screen_height = self.driver.execute_script("return window.screen.height;")
        half_width = screen_width // 2
        self.driver.set_window_position(half_width, 0)
        self.driver.set_window_size(half_width, screen_height)
        # Allow overriding the wait timeout via env var WAIT_TIMEOUT (seconds)
        self.wait_timeout = int(os.environ.get("WAIT_TIMEOUT", "30"))
        self.wait = WebDriverWait(self.driver, self.wait_timeout)

    def _wait(self, condition, locator, timeout=None, desc=None):
        """Wrapper around WebDriverWait.until that captures debug artifacts on timeout.

        condition: an expected_conditions factory like EC.visibility_of_element_located
        locator: tuple like (By.XPATH, '...')
        timeout: optional override (seconds)
        desc: short description for debug filenames and messages
        """
        timeout = timeout or self.wait_timeout
        desc = desc or (locator[1] if isinstance(locator, tuple) else str(locator))
        try:
            return WebDriverWait(self.driver, timeout).until(condition(locator))
        except TimeoutException:
            ts = time.strftime('%Y%m%d-%H%M%S')
            debug_dir = os.path.join(os.path.dirname(__file__), "debug_artifacts")
            os.makedirs(debug_dir, exist_ok=True)
            screenshot = os.path.join(debug_dir, f"{desc}-{ts}.png")
            page_file = os.path.join(debug_dir, f"{desc}-{ts}.html")
            try:
                self.driver.save_screenshot(screenshot)
            except Exception as e:
                print(f"Failed to save screenshot: {e}", flush=True)
            try:
                with open(page_file, "w", encoding="utf-8") as fh:
                    fh.write(self.driver.page_source)
            except Exception as e:
                print(f"Failed to save page source: {e}", flush=True)

            # Print helpful debug info immediately
            print(f"Timeout waiting for: {desc}", flush=True)
            print(f"Current URL: {self.driver.current_url}", flush=True)
            print(f"Saved screenshot: {screenshot}", flush=True)
            print(f"Saved page source: {page_file}", flush=True)
            raise

    def teardown_method(self, method):
        self.driver.quit()

    def test_superloop_flow(self):
        self.driver.get("https://www.swoop.com.au/cimet/?partner=CIME01/")

        # Reduce zoom to avoid overlays
        self.driver.execute_script("document.body.style.zoom='90%'")

        # ================= STEP 1: Address input =================
        address_input = self._wait(EC.visibility_of_element_located, (
            By.XPATH,
            "//*[@id='search-app']/form/div[1]/div/div/input"
        ), desc="address_input")
        address_input.send_keys(self.data["address"])
        time.sleep(2)  # Wait for dropdown to populate
        
        # Click on the first address suggestion from the dropdown
        first_suggestion = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='search-app']/form/div[1]/div/div[2]/ul/li[1]"
        ), desc="first_suggestion")
        self.driver.execute_script("arguments[0].click();", first_suggestion)
        time.sleep(1)
        print("✅ Address selected from dropdown", flush=True)

        # ================= STEP 2: Search Home Plans button =================
        home_plans_btn = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='search-app']/form/div[2]/button[1]"
        ), desc="home_plans_btn")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", home_plans_btn)
        self.driver.execute_script("arguments[0].click();", home_plans_btn)
        time.sleep(2)
        print("✅ Search Home Plans button clicked", flush=True)
 
        # ================= STEP 3: Choose NBN internet type =================
        nbn_option = self._wait(EC.presence_of_element_located, (
            By.XPATH,
            "//*[@id='service-section']/div[2]/div/div[4]"
        ), desc="nbn_option")
        self.driver.execute_script("arguments[0].click();", nbn_option)
        time.sleep(2)
        print("✅ NBN internet type selected", flush=True)

        # ================= STEP 4: Choose your speed =================
        # Speed plan mapping
        speed_plans = {
            "50/20 MBPS": "//*[@id='plan-section']/div[2]/div[1]/div[2]",
            "100/20 MBPS": "//*[@id='plan-section']/div[2]/div[1]/div[3]",
            "100/40 MBPS": "//*[@id='plan-section']/div[2]/div[1]/div[4]"
        }
        
        selected_plan = self.data["speedPlan"]
        speed_xpath = speed_plans.get(selected_plan)
        
        if not speed_xpath:
            raise ValueError(f"Invalid speed plan: {selected_plan}. Available options: {list(speed_plans.keys())}")
        
        speed_option = self._wait(EC.presence_of_element_located, (
            By.XPATH,
            speed_xpath
        ), desc=f"speed_option-{selected_plan}")
        self.driver.execute_script("arguments[0].click();", speed_option)
        time.sleep(2)
        print(f"✅ Speed option selected: {selected_plan}", flush=True)

        # ================= STEP 5: Click Checkout button =================
        checkout_btn = self._wait(EC.presence_of_element_located, (
            By.XPATH,
            "//*[@id='summary-section']/div[2]/div[2]/div/button"
        ), desc="checkout_btn")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkout_btn)
        self.driver.execute_script("arguments[0].click();", checkout_btn)
        time.sleep(3)
        print("✅ Checkout button clicked", flush=True)

        # ================= STEP 6: Enter First Name =================
        first_name_input = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='firstName']"
        ), desc="first_name_input")
        first_name_input.send_keys(self.data["firstName"])
        time.sleep(1)
        print("✅ First name entered", flush=True)

        # ================= STEP 7: Enter Last Name =================
        last_name_input = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='lastName']"
        ), desc="last_name_input")
        last_name_input.send_keys(self.data["lastName"])
        time.sleep(1)
        print("✅ Last name entered", flush=True)

        # ================= STEP 8: Enter Email =================
        email_input = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='email']"
        ), desc="email_input")
        email_input.send_keys(self.data["email"])
        time.sleep(1)
        print("✅ Email entered", flush=True)

        # ================= STEP 9: Enter Contact Number =================
        phone_input = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='phone']"
        ), desc="phone_input")
        phone_input.send_keys(self.data["contact"])
        time.sleep(1)
        print("✅ Contact number entered", flush=True)

        # ================= STEP 10: Enter Birthday =================
        birthday_input = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='birthDay']"
        ), desc="birthday_input")
        birthday_input.send_keys(self.data["dob"])
        time.sleep(1)
        print("✅ Birthday entered", flush=True)

        # ================= STEP 11: Enter Birth Month =================
        birth_month = self.data["dob"].split("/")[1]  # Extract month from dd/mm/yyyy
        month_input = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='birthMonth']"
        ), desc="birth_month_input")
        month_input.send_keys(birth_month)
        time.sleep(1)
        print("✅ Birth month entered", flush=True)

        # ================= STEP 12: Enter Birth Year =================
        birth_year = self.data["dob"].split("/")[2]  # Extract year from dd/mm/yyyy
        year_input = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='birthYear']"
        ), desc="birth_year_input")
        year_input.send_keys(birth_year)
        time.sleep(1)
        print("✅ Birth year entered", flush=True)

        # ================= STEP 13: Click Continue button =================
        continue_btn = self._wait(EC.presence_of_element_located, (
            By.XPATH,
            "//*[@id='signup-form']/div[1]/div/div[4]/button[1]"
        ), desc="continue_btn")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", continue_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", continue_btn)
        time.sleep(2)
        print("✅ Continue button clicked", flush=True)

        # ================= STEP 14: Click Checkbox =================
        checkbox = self._wait(EC.presence_of_element_located, (
            By.XPATH,
            "//*[@id='signup-form']/div[2]/div/div[3]/div[2]/label/span"
        ), desc="checkbox")
        self.driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(1)
        print("✅ Checkbox selected", flush=True)

        # ================= STEP 15: Click Review Order button =================
        review_order_btn = self._wait(EC.presence_of_element_located, (
            By.XPATH,
            "//*[@id='signup-form']/div[2]/div/div[5]/button[1]"
        ), desc="review_order_btn")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", review_order_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", review_order_btn)
        time.sleep(2)
        print("✅ Review Order button clicked", flush=True)

        # ================= STEP 19: Final confirm =================
        final_btn = self._wait(EC.presence_of_element_located, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[3]/div/button"
        ), desc="final_btn")
        self.driver.execute_script("arguments[0].click();", final_btn)
        print("✅ TEST COMPLETED SUCCESSFULLY", flush=True)
        time.sleep(5)
