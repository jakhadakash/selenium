def test_untitled(self):
    import time
    import json
    import os
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support import expected_conditions as EC

    # ================= Load JSON =================
    data_path = os.path.join(os.path.dirname(__file__), "test_data2.json")
    with open(data_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    self.driver.get("https://www.superloop.com/")
    self.driver.maximize_window()
    self.driver.execute_script("document.body.style.zoom='90%'")

    # ================= STEP 1: Address input =================
    address_input = self.wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//*[@id='gatsby-focus-wrapper']//input"
    )))
    address_input.clear()
    address_input.send_keys(data.get("address", ""))

    self.wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//*[@id='gatsby-focus-wrapper']//button"
    )))
    time.sleep(0.5)
    address_input.send_keys(Keys.ARROW_DOWN, Keys.ENTER)

    # ================= STEP 2: Suggested address =================
    button = self.wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//*[@id='gatsby-focus-wrapper']//button[1]"
    )))
    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button)
    time.sleep(0.5)
    self.driver.execute_script("arguments[0].click();", button)
    time.sleep(2)

    # ================= STEP 3: Address card =================
    card = self.wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//*[@id='gatsby-focus-wrapper']//div[contains(@class,'address')]"
    )))
    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
    self.driver.execute_script("arguments[0].click();", card)
    time.sleep(2)

    # ================= STEP 4: sqField =================
    sq = self.wait.until(EC.presence_of_element_located((
        By.ID, "sqField"
    )))
    self.driver.execute_script("arguments[0].click();", sq)
    time.sleep(2)

    # ================= STEP 5: Plan =================
    plan = self.wait.until(EC.presence_of_element_located((
        By.XPATH, "//*[@id='plans']//div[contains(@class,'plan')]"
    )))
    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", plan)
    self.driver.execute_script("arguments[0].click();", plan)
    time.sleep(3)

    # ================= STEP 6: Device =================
    device = self.wait.until(EC.presence_of_element_located((
        By.XPATH, "//*[@id='device-section']//img"
    )))
    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", device)
    self.driver.execute_script("arguments[0].click();", device)
    time.sleep(3)

    # ================= STEP 7–9: Popups =================
    for popup_xpath in [
        "/html/body/div[6]//div[contains(@class,'option')]",
        "/html/body/div[6]//div[contains(@class,'confirm')]",
        "/html/body/div[6]//div[contains(@class,'continue')]"
    ]:
        popup = self.wait.until(EC.presence_of_element_located((By.XPATH, popup_xpath)))
        self.driver.execute_script("arguments[0].click();", popup)
        time.sleep(1)

    # ================= STEP 10: Final section =================
    final_section = self.wait.until(EC.presence_of_element_located((
        By.XPATH, "//*[@id='gatsby-focus-wrapper']//div[contains(@class,'final')]"
    )))
    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", final_section)
    self.driver.execute_script("arguments[0].click();", final_section)
    time.sleep(2)

    # ================= STEP 11: Title =================
    Select(self.wait.until(EC.presence_of_element_located((
        By.XPATH, "//select"
    )))).select_by_visible_text(data.get("salutation", "Ms"))

    # ================= STEP 12–16: Form =================
    fields = {
        "firstName": "//input[@name='firstName']",
        "lastName": "//input[@name='lastName']",
        "email": "//input[@name='email']",
        "contact": "//input[@name='contact']",
        "dob": "//input[@name='dob']"
    }

    for key, xpath in fields.items():
        field = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        field.clear()
        field.send_keys(data.get(key, ""))

    # ================= STEP 17: Submit =================
    submit_btn = self.wait.until(EC.presence_of_element_located((
        By.XPATH, "//form//button"
    )))
    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
    self.driver.execute_script("arguments[0].click();", submit_btn)
    time.sleep(2)

    # ================= STEP 18: Account name =================
    account = self.wait.until(EC.presence_of_element_located((
        By.XPATH, "//input[contains(@name,'delivery')]"
    )))
    account.send_keys(data.get("deliveryName", ""))

    # ================= STEP 19: Final confirm =================
    final_btn = self.wait.until(EC.presence_of_element_located((
        By.XPATH, "//button[contains(text(),'Confirm')]"
    )))
    self.driver.execute_script("arguments[0].click();", final_btn)

    print("✅ TEST COMPLETED SUCCESSFULLY")
    time.sleep(20)
