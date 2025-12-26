from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")

print("Starting Chrome...")
driver = webdriver.Chrome(options=options)

print("Loading Superloop website...")
driver.get("https://www.superloop.com/")
time.sleep(5)

print(f"Page title: {driver.title}")
print(f"Current URL: {driver.current_url}")

try:
    print("Looking for address input...")
    address_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//*[@id='gatsby-focus-wrapper']/div/div[3]/div[1]/div/div/div/div/div[2]/div/div/div[1]/div/input"
        ))
    )
    print("✓ Address input found!")
    print(f"Is displayed: {address_input.is_displayed()}")
    print(f"Is enabled: {address_input.is_enabled()}")
    print(f"Tag name: {address_input.tag_name}")
    
    print("Trying to send keys...")
    address_input.send_keys("123 Test Street")
    print("✓ Success!")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    print(f"Exception type: {type(e).__name__}")
    driver.save_screenshot("error_screenshot.png")
    print("Screenshot saved as error_screenshot.png")

input("Press Enter to close browser...")
driver.quit()