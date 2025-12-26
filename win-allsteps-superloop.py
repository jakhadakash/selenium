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
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(stream_handler)

        self.logger = logging.getLogger(__name__)
        
        self.logger.info("=" * 80)
        self.logger.info("INITIALIZING TEST SETUP")
        self.logger.info("=" * 80)
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        # Windows-specific options
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
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

    def _wait_and_interact(self, xpath, desc, action="click", input_value=None, timeout=60):
        """
        Universal method to wait for element and interact with it (Windows-compatible).
        
        Args:
            xpath: XPath selector for the element
            desc: Description for logging
            action: "click", "input", or "select"
            input_value: Value to input (for input/select actions)
            timeout: Wait timeout in seconds
        """
        self.logger.info(f"Step: {desc}")
        
        # Wait for presence
        self.logger.info(f"  Waiting for element presence...")
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        self.logger.info(f"  Element present in DOM")
        
        # Wait for visibility (if needed for interaction)
        if action in ["click", "input"]:
            self.logger.info(f"  Waiting for element visibility...")
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            self.logger.info(f"  Element visible")
        
        # Scroll into view
        self.logger.info(f"  Scrolling element into view...")
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center', behavior:'instant'});", element)
        time.sleep(1)
        
        # Remove overlays
        self.driver.execute_script("""
            var overlays = document.querySelectorAll('[class*="overlay"], [class*="modal"], [id*="overlay"]');
            overlays.forEach(function(el) { 
                if (el.style.display !== 'none') {
                    el.style.display = 'none'; 
                }
            });
        """)
        time.sleep(0.5)
        
        # Perform action
        if action == "click":
            self.logger.info(f"  Clicking element...")
            try:
                element.click()
                self.logger.info(f"  Clicked via regular click()")
            except Exception as e:
                self.logger.warning(f"  Regular click failed: {e}, using JavaScript...")
                self.driver.execute_script("arguments[0].click();", element)
                self.logger.info(f"  Clicked via JavaScript")
            time.sleep(1)
            
        elif action == "input":
            self.logger.info(f"  Setting focus and entering value...")
            # Force focus
            try:
                element.click()
            except:
                self.driver.execute_script("arguments[0].click();", element)
            
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].focus();", element)
            time.sleep(0.5)
            
            # Clear field
            try:
                element.clear()
            except:
                self.driver.execute_script("arguments[0].value = '';", element)
            time.sleep(0.5)
            
            # Input value
            try:
                element.send_keys(input_value)
                self.logger.info(f"  Value entered via send_keys: {input_value}")
            except Exception as e:
                self.logger.warning(f"  send_keys failed: {e}, using JavaScript...")
                self.driver.execute_script(
                    "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true})); arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                    element,
                    input_value
                )
                self.logger.info(f"  Value entered via JavaScript: {input_value}")
            time.sleep(1)
            
        elif action == "select":
            self.logger.info(f"  Selecting dropdown value: {input_value}")
            Select(element).select_by_visible_text(input_value)
            self.logger.info(f"  Value selected")
            time.sleep(1)
        
        self.logger.info(f"  [OK] {desc} completed\n")
        return element

    def _wait(self, condition, locator, timeout=None, desc=None):
        """Wrapper around WebDriverWait.until that captures debug artifacts on timeout."""
        timeout = timeout or 30
        desc = desc or (locator[1] if isinstance(locator, tuple) else str(locator))
        
        self.logger.info(f"Waiting for: {desc} (timeout: {timeout}s)")
        
        try:
            element = WebDriverWait(self.driver, timeout).until(condition(locator))
            self.logger.info(f"Found: {desc}")
            return element
        except TimeoutException as te:
            ts = time.strftime('%Y%m%d-%H%M%S')
            debug_dir = os.path.join(os.path.dirname(__file__), "debug_artifacts")
            os.makedirs(debug_dir, exist_ok=True)
            screenshot = os.path.join(debug_dir, f"{desc}-{ts}.png")
            page_file = os.path.join(debug_dir, f"{desc}-{ts}.html")
            
            try:
                self.driver.save_screenshot(screenshot)
                self.logger.error(f"Saved screenshot: {screenshot}")
            except Exception as e:
                self.logger.error(f"Failed to save screenshot: {e}")
            
            try:
                with open(page_file, "w", encoding="utf-8") as fh:
                    fh.write(self.driver.page_source)
                self.logger.error(f"Saved page source: {page_file}")
            except Exception as e:
                self.logger.error(f"Failed to save page source: {e}")

            self.logger.error(f"TIMEOUT waiting for: {desc}")
            self.logger.error(f"Current URL: {self.driver.current_url}")
            self.logger.error(f"Page title: {self.driver.title}")
            
            raise
        except Exception as e:
            self.logger.error(f"ERROR waiting for {desc}: {str(e)}")
            self.logger.error(f"Exception type: {type(e).__name__}")
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
        self.logger.info("[OK] Page loaded successfully")
        
        if os.environ.get("FULLSCREEN"):
            self.logger.info("FULLSCREEN env var set - maximizing window...")
            self.driver.maximize_window()
            self.logger.info("[OK] Window maximized")
        else:
            self.logger.info("Leaving window at the half-screen size configured in setup")

        # Reduce zoom to avoid overlays
        self.logger.info("Adjusting page zoom to 90%")
        self.driver.execute_script("document.body.style.zoom='90%'")
        self.logger.info("[OK] Zoom adjusted\n")

        # ================= STEP 1: Address input =================
        address_value = data.get("address", "")
        self._wait_and_interact(
            xpath="/html/body/div[1]/div[1]/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[1]/div/input",
            desc="Entering address",
            action="input",
            input_value=address_value
        )
        
        # Wait for and click the first suggestion
        time.sleep(1)
        self._wait_and_interact(
            xpath="//*[@id='gatsby-focus-wrapper']//button[1]",
            desc="Selecting first address suggestion",
            action="click at"
        )
        
        # Log Residential button xpath without clicking
        time.sleep(2)
        residential_xpath = "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[2]/div[1]"
        self.logger.info(f"RESIDENTIAL BUTTON XPATH: {residential_xpath}")
        self.logger.info("Note: Not clicking Residential button - xpath logged only\n")

        # ================= STEP 2: Suggested address button =================
        self._wait_and_interact(
            xpath="//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[2]/div/button[1]",
            desc="Clicking suggested address button",
            action="click"
        )
        time.sleep(1)

        # ================= STEP 3: Address card =================
        self._wait_and_interact(
            xpath="//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div[1]",
            desc="Clicking address card",
            action="click"
        )
        time.sleep(2)

        # ================= STEP 4: sqField =================
        self._wait_and_interact(
            xpath="//*[@id='sqField']/div/div[2]/div/div[1]/div/div",
            desc="Clicking sqField",
            action="click"
        )
        time.sleep(2)

        # ================= STEP 5: Plan =================
        self._wait_and_interact(
            xpath="//*[@id='plans']/div/div[1]/div/div[1]/div/div/div[5]/div",
            desc="Selecting plan",
            action="click"
        )
        time.sleep(3)

        # ================= STEP 6: Device =================
        self._wait_and_interact(
            xpath="//*[@id='device-section']/div/div/div[2]/div/div/div/img",
            desc="Selecting device",
            action="click"
        )
        time.sleep(3)

        # ================= STEP 7-9: Popup flow =================
        self._wait_and_interact(
            xpath="/html/body/div[6]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div[1]/div/div",
            desc="Handling popup 1",
            action="click"
        )
        time.sleep(1)

        self._wait_and_interact(
            xpath="/html/body/div[6]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[3]/div[2]",
            desc="Handling popup 2",
            action="click"
        )
        time.sleep(1)

        self._wait_and_interact(
            xpath="/html/body/div[6]/div/div/div[3]/div/div",
            desc="Handling popup 3",
            action="click"
        )
        time.sleep(2)

        # ================= STEP 10: Final section =================
        self._wait_and_interact(
            xpath="//*[@id='gatsby-focus-wrapper']/div/div[6]/div/div/div[2]/div/div/div[5]",
            desc="Clicking final section",
            action="click"
        )
        time.sleep(2)

        # ================= STEP 11: Title/Salutation =================
        salutation_value = data.get("salutation", "Ms")
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[1]/div/div/select",
            desc=f"Selecting salutation: {salutation_value}",
            action="select",
            input_value=salutation_value
        )

        # ================= STEP 12: First Name =================
        first_name = data.get("firstName", "")
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[2]/div/div/input",
            desc="Entering first name",
            action="input",
            input_value=first_name
        )

        # ================= STEP 13: Last Name =================
        last_name = data.get("lastName", "")
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[3]/div/div/input",
            desc="Entering last name",
            action="input",
            input_value=last_name
        )

        # ================= STEP 14: Email =================
        email = data.get("email", "")
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[4]/div/div/input",
            desc="Entering email",
            action="input",
            input_value=email
        )

        # ================= STEP 15: Contact Number =================
        contact = data.get("contact", "")
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[5]/div/div/input",
            desc="Entering contact number",
            action="input",
            input_value=contact
        )

        # ================= STEP 16: Date of Birth =================
        dob = data.get("dob", "")
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[6]/div/div/input",
            desc="Entering date of birth",
            action="input",
            input_value=dob
        )

        # ================= STEP 17: Submit Form =================
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/button",
            desc="Submitting form",
            action="click"
        )
        time.sleep(2)

        # ================= STEP 18: Delivery/Account Name =================
        delivery_name = data.get("deliveryName", "")
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[2]/div/div[1]/div/div/input",
            desc="Entering delivery/account name",
            action="input",
            input_value=delivery_name
        )
        time.sleep(1)

        # ================= STEP 19: Final Confirmation =================
        self._wait_and_interact(
            xpath="//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[3]/div/button",
            desc="Final confirmation",
            action="click"
        )

        self.logger.info("\n" + "=" * 80)
        self.logger.info("[OK] TEST COMPLETED SUCCESSFULLY")
        self.logger.info("=" * 80)
        self.logger.info("Logs are printed to the terminal (stdout)")
        
        print("\n[OK] TEST COMPLETED SUCCESSFULLY")
        time.sleep(30)