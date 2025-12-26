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
        data_file = os.path.join(os.path.dirname(__file__), "test_data2.json")
        with open(data_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        # ================= Chrome Setup =================
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Position window on left half of screen
        screen_width = self.driver.execute_script("return window.screen.width;")
        screen_height = self.driver.execute_script("return window.screen.height;")
        half_width = screen_width // 2
        self.driver.set_window_position(0, 0)
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
        self.driver.get("https://www.superloop.com/")

        # Check for FULLSCREEN environment variable
        if os.environ.get("FULLSCREEN"):
            self.driver.maximize_window()
            print("✅ Window maximized", flush=True)

        # Reduce zoom to avoid overlays
        self.driver.execute_script("document.body.style.zoom='90%'")

        # ================= STEP 1: Address input =================
        address_input = self._wait(EC.visibility_of_element_located, (
            By.XPATH,
            "/html/body/div[1]/div[1]/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[1]/div/input"
        ), desc="address_input")
        address_input.send_keys(self.data["address"])
        time.sleep(1)
        print("✅ Address entered", flush=True)
        
        # Click on the first address suggestion
        first_suggestion = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']//button[1]"
        ), desc="first_suggestion")
        self.driver.execute_script("arguments[0].click();", first_suggestion)
        time.sleep(2)
        print("✅ First address suggestion selected", flush=True)

        # Log Residential button xpath without clicking
        residential_xpath = "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[2]/div[1]"
        print(f"ℹ️ RESIDENTIAL BUTTON XPATH: {residential_xpath}", flush=True)

        # ================= STEP 2: Suggested address button =================
        suggested_btn = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[2]/div/button[1]"
        ), desc="suggested_btn")
        self.driver.execute_script("arguments[0].click();", suggested_btn)
        time.sleep(1)
        print("✅ Suggested address button clicked", flush=True)

        # ================= STEP 3: Address card =================
        address_card = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div[1]"
        ), desc="address_card")
        self.driver.execute_script("arguments[0].click();", address_card)
        time.sleep(2)
        print("✅ Address card clicked", flush=True)

        # ================= STEP 4: sqField =================
        sq_field = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='sqField']/div/div[2]/div/div[1]/div/div"
        ), desc="sq_field")
        self.driver.execute_script("arguments[0].click();", sq_field)
        time.sleep(2)
        print("✅ sqField clicked", flush=True)

        # ================= STEP 5: Plan selection =================
        plan = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='plans']/div/div[1]/div/div[1]/div/div/div[5]/div"
        ), desc="plan")
        self.driver.execute_script("arguments[0].click();", plan)
        time.sleep(3)
        print("✅ Plan selected", flush=True)

        # ================= STEP 6: Device selection =================
        device = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='device-section']/div/div/div[2]/div/div/div/img"
        ), desc="device")
        self.driver.execute_script("arguments[0].click();", device)
        time.sleep(3)
        print("✅ Device selected", flush=True)

        # ================= STEP 7-9: Popup flow =================
        popup1 = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "/html/body/div[6]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div[1]/div/div"
        ), desc="popup1")
        self.driver.execute_script("arguments[0].click();", popup1)
        time.sleep(1)
        print("✅ Popup 1 handled", flush=True)

        popup2 = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "/html/body/div[6]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[3]/div[2]"
        ), desc="popup2")
        self.driver.execute_script("arguments[0].click();", popup2)
        time.sleep(1)
        print("✅ Popup 2 handled", flush=True)

        popup3 = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "/html/body/div[6]/div/div/div[3]/div/div"
        ), desc="popup3")
        self.driver.execute_script("arguments[0].click();", popup3)
        time.sleep(2)
        print("✅ Popup 3 handled", flush=True)

        # ================= STEP 10: Final section =================
        final_section = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[6]/div/div/div[2]/div/div/div[5]"
        ), desc="final_section")
        self.driver.execute_script("arguments[0].click();", final_section)
        time.sleep(2)
        print("✅ Final section clicked", flush=True)

        # ================= STEP 11: Salutation/Title =================
        salutation = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[1]/div/div/select"
        ), desc="salutation")
        Select(salutation).select_by_visible_text(self.data["salutation"])
        time.sleep(1)
        print(f"✅ Salutation selected: {self.data['salutation']}", flush=True)

        # ================= STEP 12: First Name =================
        first_name = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[2]/div/div/input"
        ), desc="first_name")
        first_name.send_keys(self.data["firstName"])
        time.sleep(1)
        print("✅ First name entered", flush=True)

        # ================= STEP 13: Last Name =================
        last_name = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[3]/div/div/input"
        ), desc="last_name")
        last_name.send_keys(self.data["lastName"])
        time.sleep(1)
        print("✅ Last name entered", flush=True)

        # ================= STEP 14: Email =================
        email = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[4]/div/div/input"
        ), desc="email")
        email.send_keys(self.data["email"])
        time.sleep(1)
        print("✅ Email entered", flush=True)

        # ================= STEP 15: Contact Number =================
        contact = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[5]/div/div/input"
        ), desc="contact")
        contact.send_keys(self.data["contact"])
        time.sleep(1)
        print("✅ Contact number entered", flush=True)

        # ================= STEP 16: Date of Birth =================
        dob = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[6]/div/div/input"
        ), desc="dob")
        dob.send_keys(self.data["dob"])
        time.sleep(1)
        print("✅ Date of birth entered", flush=True)

        # ================= STEP 17: Submit Form =================
        submit_btn = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/button"
        ), desc="submit_btn")
        self.driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        print("✅ Form submitted", flush=True)

        # ================= STEP 18: Delivery/Account Name =================
        delivery_name = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[2]/div/div[1]/div/div/input"
        ), desc="delivery_name")
        delivery_name.send_keys(self.data["deliveryName"])
        time.sleep(1)
        print("✅ Delivery/Account name entered", flush=True)

        # ================= STEP 19: Final Confirmation =================
        final_btn = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[3]/div/button"
        ), desc="final_btn")
        self.driver.execute_script("arguments[0].click();", final_btn)
        print("✅ TEST COMPLETED SUCCESSFULLY", flush=True)
        time.sleep(30)