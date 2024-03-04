from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")  # Bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
options.add_argument("--disable-gpu")  # Applicable to windows os only
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

driver = webdriver.Chrome(options=options)

# Load the page
driver.get("http://172.30.134.22:8050/prod_eff")

# Wait for a certain time or until a specific condition is met
time.sleep(10)  # Wait for 10 seconds
# Or use WebDriverWait for more precise waiting conditions

# Save the page source to a file
with open("pageofwcreport.html", "w", encoding='utf-8') as f:
    f.write(driver.page_source)

# Clean up
driver.quit()