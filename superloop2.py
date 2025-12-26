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
        
        # Position window on right half of screen
        screen_width = self.driver.execute_script("return window.screen.width;")
        screen_height = self.driver.execute_script("return window.screen.height;")
        half_width = screen_width // 2
        self.driver.set_window_position(half_width, 0)
        self.driver.set_window_size(half_width, screen_height)
        self.wait = WebDriverWait(self.driver, 30)

    def teardown_method(self, method):
        self.driver.quit()

    def test_superloop_flow(self):
        self.driver.get("https://www.superloop.com/")

        # Reduce zoom to avoid overlays
        self.driver.execute_script("document.body.style.zoom='90%'")

        # ================= STEP 1: Address input =================
        address_input = self.wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[1]/div/input"
        )))
        address_input.send_keys(self.data["address"])
        time.sleep(2)  # Wait for dropdown to populate
        
        # Click on the first address suggestion from the dropdown
        first_suggestion = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[2]/div/button[1]"
        )))
        self.driver.execute_script("arguments[0].click();", first_suggestion)
        time.sleep(1)
        print("✅ Address selected from dropdown")

        # ================= STEP 2: Click Residential option =================
        time.sleep(2)  # Wait before selecting residential
        residential_option = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div[1]"
        )))
        self.driver.execute_script("arguments[0].click();", residential_option)
        time.sleep(1)
        print("✅ Residential option selected")

        # ================= STEP 2: Build Your Plan button =================
        build_plan_btn = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='address-success-days']/div/a"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", build_plan_btn)
        self.driver.execute_script("arguments[0].click();", build_plan_btn)
        time.sleep(2)
        print("✅ Build Your Plan button clicked")
 
        # ================= STEP 3: Choose your speed =================
        # Speed plan mapping for Tangerine
        speed_plans = {
            "25 MBPS/8.5 MBPS": "//*[@id='75_speed']",
            "50 MBPS/17MBPS": "//*[@id='74_speed']",
            "500 MBPS/42.5MBPS": "//*[@id='72_speed']",
            "700 MBPS/85MBPS": "//*[@id='70_speed']"
        }
        
        selected_plan = self.data["speedPlan"]
        speed_xpath = speed_plans.get(selected_plan)
        
        if not speed_xpath:
            raise ValueError(f"Invalid speed plan: {selected_plan}. Available options: {list(speed_plans.keys())}")
        
        speed_option = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            speed_xpath
        )))
        self.driver.execute_script("arguments[0].click();", speed_option)
        time.sleep(2)
        print(f"✅ Speed option selected: {selected_plan}")

        # ================= STEP 5: Click Checkout button =================
        checkout_btn = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='summary-section']/div[2]/div[2]/div/button"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", checkout_btn)
        self.driver.execute_script("arguments[0].click();", checkout_btn)
        time.sleep(3)
        print("✅ Checkout button clicked")

        # ================= STEP 6: Enter First Name =================
        first_name_input = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='firstName']"
        )))
        first_name_input.send_keys(self.data["firstName"])
        time.sleep(1)
        print("✅ First name entered")

        # ================= STEP 7: Enter Last Name =================
        last_name_input = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='lastName']"
        )))
        last_name_input.send_keys(self.data["lastName"])
        time.sleep(1)
        print("✅ Last name entered")

        # ================= STEP 8: Enter Email =================
        email_input = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='email']"
        )))
        email_input.send_keys(self.data["email"])
        time.sleep(1)
        print("✅ Email entered")

        # ================= STEP 9: Enter Contact Number =================
        phone_input = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='phone']"
        )))
        phone_input.send_keys(self.data["contact"])
        time.sleep(1)
        print("✅ Contact number entered")

        # ================= STEP 10: Enter Birthday =================
        birthday_input = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='birthDay']"
        )))
        birthday_input.send_keys(self.data["dob"])
        time.sleep(1)
        print("✅ Birthday entered")

        # ================= STEP 11: Enter Birth Month =================
        birth_month = self.data["dob"].split("/")[1]  # Extract month from dd/mm/yyyy
        month_input = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='birthMonth']"
        )))
        month_input.send_keys(birth_month)
        time.sleep(1)
        print("✅ Birth month entered")

        # ================= STEP 12: Enter Birth Year =================
        birth_year = self.data["dob"].split("/")[2]  # Extract year from dd/mm/yyyy
        year_input = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='birthYear']"
        )))
        year_input.send_keys(birth_year)
        time.sleep(1)
        print("✅ Birth year entered")

        # ================= STEP 13: Click Continue button =================
        continue_btn = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='signup-form']/div[1]/div/div[4]/button[1]"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", continue_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", continue_btn)
        time.sleep(2)
        print("✅ Continue button clicked")

        # ================= STEP 14: Click Checkbox =================
        checkbox = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='signup-form']/div[2]/div/div[3]/div[2]/label/span"
        )))
        self.driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(1)
        print("✅ Checkbox selected")

        # ================= STEP 15: Click Review Order button =================
        review_order_btn = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='signup-form']/div[2]/div/div[5]/button[1]"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", review_order_btn)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", review_order_btn)
        time.sleep(2)
        print("✅ Review Order button clicked")

        # ================= STEP 19: Final confirm =================
        final_btn = self.wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='root']/div[2]/div/div/div/div[1]/div/div[2]/div/form/div[2]/div[3]/div/button"
        )))
        self.driver.execute_script("arguments[0].click();", final_btn)

        print("✅ TEST COMPLETED SUCCESSFULLY")
        time.sleep(5)
