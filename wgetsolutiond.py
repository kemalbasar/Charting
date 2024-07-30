from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()

driver = webdriver.Chrome(options=options)

# Load the page
driver.get("http://172.30.134.22:8050/adrcncmonth")

# Wait for a certain time or until a specific condition is met
time.sleep(120)  # Wait for 10 seconds
# Or use WebDriverWait for more precise waiting conditions

# Save the page source to a file
with open("pageofwcreport.html", "w", encoding='utf-8') as f:
    f.write(driver.page_source)

# Clean up
driver.quit()