import pytest
import time
import json
import os
import logging
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException


class TestUntitled():

    def setup_method(self, method):
        # Configure logging so output is available both on stdout and in a file
        log_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        )

        root_logger = logging.getLogger()
        # Remove any existing handlers to avoid duplicate logs when pytest reuses the process
        for h in list(root_logger.handlers):
            root_logger.removeHandler(h)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(log_formatter)

        # Only add a stream handler so logs appear on the terminal (stdout).
        # If you later want file logging, add a FileHandler here or set an env var.
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(stream_handler)

        self.logger = logging.getLogger(__name__)
        
        self.logger.info("=" * 80)
        self.logger.info("INITIALIZING TEST SETUP")
        self.logger.info("=" * 80)
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        self.logger.info("Creating Chrome WebDriver instance...")
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Set window to half screen (left side)
        screen_width = self.driver.execute_script("return window.screen.availWidth")
        screen_height = self.driver.execute_script("return window.screen.availHeight")
        
        half_width = screen_width // 2
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(half_width, screen_height)
        
        self.logger.info(f"Browser window set to half screen: {half_width}x{screen_height}")
        
        self.wait = WebDriverWait(self.driver, 30)
        self.logger.info("WebDriverWait configured with 30 second timeout")
        self.logger.info("Setup completed successfully\n")

    def teardown_method(self, method):
        self.logger.info("\n" + "=" * 80)
        self.logger.info("TEARING DOWN TEST")
        self.logger.info("=" * 80)
        self.logger.info("Closing browser...")
        self.driver.quit()
        self.logger.info("Browser closed successfully")

    def _wait(self, condition, locator, timeout=None, desc=None):
        """Wrapper around WebDriverWait.until that captures debug artifacts on timeout."""
        timeout = timeout or 30
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
                self.logger.error(f"Failed to save screenshot: {e}")
            try:
                with open(page_file, "w", encoding="utf-8") as fh:
                    fh.write(self.driver.page_source)
            except Exception as e:
                self.logger.error(f"Failed to save page source: {e}")

            self.logger.error(f"Timeout waiting for: {desc}")
            self.logger.error(f"Current URL: {self.driver.current_url}")
            self.logger.error(f"Saved screenshot: {screenshot}")
            self.logger.error(f"Saved page source: {page_file}")
            raise

    def test_untitled(self):
        self.logger.info("\n" + "=" * 80)
        self.logger.info("STARTING TEST EXECUTION")
        self.logger.info("=" * 80)
        
        # Load test data from JSON file located next to this script
        data_path = os.path.join(os.path.dirname(__file__), "test_data2.json")
        self.logger.info(f"Loading test data from: {data_path}")
        
        with open(data_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        
        self.logger.info(f"Test data loaded successfully: {len(data)} fields found")
        self.logger.info(f"Test data keys: {list(data.keys())}\n")

        self.logger.info("STEP 0: Navigating to Superloop website")
        self.driver.get("https://www.superloop.com/")
        self.logger.info("✓ Page loaded successfully")
        
        # Keep the browser at the half-screen size configured in setup to avoid
        # forcing a full-screen window. If you want fullscreen, set env var
        # FULLSCREEN=1 when running the test and it'll maximize instead.
        if os.environ.get("FULLSCREEN"):
            self.logger.info("FULLSCREEN env var set — maximizing window...")
            self.driver.maximize_window()
            self.logger.info("✓ Window maximized")
        else:
            self.logger.info("Leaving window at the half-screen size configured in setup")

        # Reduce zoom to avoid overlays
        self.logger.info("Adjusting page zoom to 90%")
        self.driver.execute_script("document.body.style.zoom='90%'")
        self.logger.info("✓ Zoom adjusted\n")

        # ================= STEP 1: Address input =================
        self.logger.info("STEP 1: Locating address input field")
        address_input = self._wait(EC.visibility_of_element_located, (
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[1]/div/input"
        ), desc="address_input")
        self.logger.info("✓ Address input field located")

        address_value = data.get("address", "")
        self.logger.info(f"Clearing and entering address: {address_value}")
        address_input.clear()
        address_input.send_keys(address_value)
        self.logger.info("✓ Address entered")

        # wait for and click the first suggestion (more robust than arrow keys)
        self.logger.info("Waiting for first suggestion to be clickable...")
        first_suggestion = self._wait(EC.element_to_be_clickable, (
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']//button[1]"
        ), desc="first_suggestion")
        self.driver.execute_script("arguments[0].click();", first_suggestion)
        time.sleep(1)
        self.logger.info("✓ Address selected from dropdown\n")

        # ================= STEP 2: Suggested address button (JS click) =================
        self.logger.info("STEP 2: Locating suggested address button")
        button = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[2]/div/button[1]"
        )))
        self.logger.info("✓ Suggested address button located")

        self.logger.info("Scrolling button into view...")
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", button
        )
        time.sleep(0.5)
        
        self.logger.info("Clicking button using JavaScript...")
        self.driver.execute_script("arguments[0].click();", button)
        self.logger.info("✓ Button clicked successfully\n")

        # ================= STEP 3: Address card =================
        self.logger.info("STEP 3: Locating address card")
        card = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div[1]"
        )))
        self.logger.info("✓ Address card located")
        
        self.logger.info("Clicking address card...")
        self.driver.execute_script("arguments[0].click();", card)
        time.sleep(2)
        self.logger.info("✓ Address card clicked\n")

        # ================= STEP 4: sqField =================
        self.logger.info("STEP 4: Locating sqField element")
        sq = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='sqField']/div/div[2]/div/div[1]/div/div"
        )))
        self.logger.info("✓ sqField element located")
        
        self.logger.info("Clicking sqField...")
        self.driver.execute_script("arguments[0].click();", sq)
        time.sleep(2)
        self.logger.info("✓ sqField clicked\n")

        # ================= STEP 5: Plan =================
        self.logger.info("STEP 5: Locating plan selection")
        plan = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='plans']/div/div[1]/div/div[1]/div/div/div[5]/div"
        )))
        self.logger.info("✓ Plan element located")
        
        self.logger.info("Selecting plan...")
        self.driver.execute_script("arguments[0].click();", plan)
        time.sleep(3)
        self.logger.info("✓ Plan selected\n")

        # ================= STEP 6: Device =================
        self.logger.info("STEP 6: Locating device selection")
        device = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='device-section']/div/div/div[2]/div/div/div/img"
        )))
        self.logger.info("✓ Device element located")
        
        self.logger.info("Selecting device...")
        self.driver.execute_script("arguments[0].click();", device)
        time.sleep(3)
        self.logger.info("✓ Device selected\n")

        # ================= STEP 7-9: Popup flow =================
        self.logger.info("STEP 7: Handling first popup")
        popup1 = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "/html/body/div[6]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div[1]/div/div"
        )))
        self.logger.info("✓ Popup 1 located")
        
        self.driver.execute_script("arguments[0].click();", popup1)
        time.sleep(1)
        self.logger.info("✓ Popup 1 clicked\n")

        self.logger.info("STEP 8: Handling second popup")
        popup2 = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "/html/body/div[6]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[3]/div[2]"
        )))
        self.logger.info("✓ Popup 2 located")
        
        self.driver.execute_script("arguments[0].click();", popup2)
        time.sleep(1)
        self.logger.info("✓ Popup 2 clicked\n")

        self.logger.info("STEP 9: Handling third popup")
        popup3 = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "/html/body/div[6]/div/div/div[3]/div/div"
        )))
        self.logger.info("✓ Popup 3 located")
        
        self.driver.execute_script("arguments[0].click();", popup3)
        time.sleep(2)
        self.logger.info("✓ Popup 3 clicked\n")

        # ================= STEP 10: Final section =================
        self.logger.info("STEP 10: Locating final section")
        final_section = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[6]/div/div/div[2]/div/div/div[5]"
        )))
        self.logger.info("✓ Final section located")
        
        self.logger.info("Clicking final section...")
        self.driver.execute_script("arguments[0].click();", final_section)
        time.sleep(2)
        self.logger.info("✓ Final section clicked\n")

        # ================= STEP 11: Title =================
        self.logger.info("STEP 11: Selecting title/salutation")
        salutation_value = data.get("salutation", "Ms")
        self.logger.info(f"Selecting: {salutation_value}")
        
        Select(self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[1]/div/div/select"
        )))).select_by_visible_text(salutation_value)
        self.logger.info("✓ Salutation selected\n")

        # ================= STEP 12-16: Form fields =================
        self.logger.info("STEP 12: Entering first name")
        first_name = data.get("firstName", "")
        self.logger.info(f"First name: {first_name}")
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[2]/div/div/input"
        ))).send_keys(first_name)
        self.logger.info("✓ First name entered\n")

        self.logger.info("STEP 13: Entering last name")
        last_name = data.get("lastName", "")
        self.logger.info(f"Last name: {last_name}")
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[3]/div/div/input"
        ))).send_keys(last_name)
        self.logger.info("✓ Last name entered\n")

        self.logger.info("STEP 14: Entering email")
        email = data.get("email", "")
        self.logger.info(f"Email: {email}")
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[4]/div/div/input"
        ))).send_keys(email)
        self.logger.info("✓ Email entered\n")

        self.logger.info("STEP 15: Entering contact number")
        contact = data.get("contact", "")
        self.logger.info(f"Contact: {contact}")
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[5]/div/div/input"
        ))).send_keys(contact)
        self.logger.info("✓ Contact number entered\n")

        self.logger.info("STEP 16: Entering date of birth")
        dob = data.get("dob", "")
        self.logger.info(f"DOB: {dob}")
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[6]/div/div/input"
        ))).send_keys(dob)
        self.logger.info("✓ Date of birth entered\n")

        # ================= STEP 17: Submit form (JS click FIX) =================
        self.logger.info("STEP 17: Submitting form")
        submit_btn = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/button"
        )))
        self.logger.info("✓ Submit button located")
        
        self.logger.info("Scrolling submit button into view...")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
        time.sleep(1)
        
        self.logger.info("Clicking submit button...")
        self.driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        self.logger.info("✓ Form submitted\n")

        # ================= STEP 18: Account name =================
        self.logger.info("STEP 18: Entering delivery/account name")
        delivery_name = data.get("deliveryName", "")
        self.logger.info(f"Delivery name: {delivery_name}")
        
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[2]/div/div[1]/div/div/input"
        ))).send_keys(delivery_name)
        time.sleep(1)
        self.logger.info("✓ Delivery name entered\n")

        # ================= STEP 19: Final confirm =================
        self.logger.info("STEP 19: Final confirmation")
        final_btn = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[3]/div/button"
        )))
        self.logger.info("✓ Final confirmation button located")
        
        self.logger.info("Clicking final confirmation button...")
        self.driver.execute_script("arguments[0].click();", final_btn)
        self.logger.info("✓ Final confirmation clicked")

        self.logger.info("\n" + "=" * 80)
        self.logger.info("✅ TEST COMPLETED SUCCESSFULLY")
        self.logger.info("=" * 80)
        self.logger.info("Logs are printed to the terminal (stdout)")
        
        print("\n✅ TEST COMPLETED SUCCESSFULLY")
        time.sleep(30)