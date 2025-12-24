# ================= STEP 1: Address input =================
address_input = self.wait.until(EC.visibility_of_element_located((
    By.XPATH,
    "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[1]/div/input"
)))

address_input.clear()
address_input.send_keys(data.get("address", ""))

# wait until suggestion buttons appear
self.wait.until(EC.presence_of_element_located((
    By.XPATH,
    "//*[@id='gatsby-focus-wrapper']//button"
)))

time.sleep(0.5)
address_input.send_keys(Keys.ARROW_DOWN, Keys.ENTER)

# ================= STEP 2: Suggested address button (JS click) =================
button = self.wait.until(EC.presence_of_element_located((
    By.XPATH,
    "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div[2]/div/button[1]"
)))

self.driver.execute_script(
    "arguments[0].scrollIntoView({block:'center'});", button
)
time.sleep(0.5)
self.driver.execute_script("arguments[0].click();", button)
