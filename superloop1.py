import pytest
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestUntitled():

    def setup_method(self, method):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install())
        )
        self.wait = WebDriverWait(self.driver, 30)

    def teardown_method(self, method):
        self.driver.quit()

    def test_untitled(self):
        # Load test data from JSON file located next to this script
        data_path = os.path.join(os.path.dirname(__file__), "test_data2.json")
        with open(data_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        self.driver.get("https://www.superloop.com/")
        self.driver.maximize_window()

        # Reduce zoom to avoid overlays
        self.driver.execute_script("document.body.style.zoom='90%'")

        # ================= STEP 1: Address input =================
        address_input = self.wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[1]/div/input"
        )))
        address_input.send_keys(data.get("address", ""))
        time.sleep(1)
        address_input.send_keys(Keys.ARROW_DOWN, Keys.ENTER)

        # ================= STEP 2: Suggested address =================
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[2]/div/button[1]"
        ))).click()
        time.sleep(2)

        # ================= STEP 3: Address card =================
        card = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div[1]"
        )))
        self.driver.execute_script("arguments[0].click();", card)
        time.sleep(2)

        # ================= STEP 4: sqField =================
        sq = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='sqField']/div/div[2]/div/div[1]/div/div"
        )))
        self.driver.execute_script("arguments[0].click();", sq)
        time.sleep(2)

        # ================= STEP 5: Plan =================
        plan = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='plans']/div/div[1]/div/div[1]/div/div/div[5]/div"
        )))
        self.driver.execute_script("arguments[0].click();", plan)
        time.sleep(3)

        # ================= STEP 6: Device =================
        device = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='device-section']/div/div/div[2]/div/div/div/img"
        )))
        self.driver.execute_script("arguments[0].click();", device)
        time.sleep(3)

        # ================= STEP 7–9: Popup flow =================
        popup1 = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "/html/body/div[6]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div[1]/div/div"
        )))
        self.driver.execute_script("arguments[0].click();", popup1)
        time.sleep(1)

        popup2 = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "/html/body/div[6]/div/div/div[2]/div[3]/div/div[2]/div[2]/div[3]/div[3]/div[2]"
        )))
        self.driver.execute_script("arguments[0].click();", popup2)
        time.sleep(1)

        popup3 = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "/html/body/div[6]/div/div/div[3]/div/div"
        )))
        self.driver.execute_script("arguments[0].click();", popup3)
        time.sleep(2)

        # ================= STEP 10: Final section =================
        final_section = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[6]/div/div/div[2]/div/div/div[5]"
        )))
        self.driver.execute_script("arguments[0].click();", final_section)
        time.sleep(2)

        # ================= STEP 11: Title =================
        Select(self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[1]/div/div/select"
        )))).select_by_visible_text(data.get("salutation", "Ms"))

        # ================= STEP 12–16: Form fields =================
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[2]/div/div/input"
        ))).send_keys(data.get("firstName", ""))

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[3]/div/div/input"
        ))).send_keys(data.get("lastName", ""))

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[4]/div/div/input"
        ))).send_keys(data.get("email", ""))

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[5]/div/div/input"
        ))).send_keys(data.get("contact", ""))

        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/div/div/div[6]/div/div/input"
        ))).send_keys(data.get("dob", ""))

        # ================= STEP 17: Submit form (JS click FIX) =================
        submit_btn = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/div[2]/div/form/button"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)

        # ================= STEP 18: Account name =================
        self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[2]/div/div[1]/div/div/input"
        ))).send_keys(data.get("deliveryName", ""))
        time.sleep(1)

        # ================= STEP 19: Final confirm =================
        final_btn = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[3]/div/button"
        )))
        self.driver.execute_script("arguments[0].click();", final_btn)

        print("✅ TEST COMPLETED SUCCESSFULLY")
        time.sleep(30)
