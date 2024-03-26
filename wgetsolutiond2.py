from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




driver = webdriver.Chrome(options=Options())

# Example: Wait for an element to be loaded
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "dynamicElement")))

# Now capture the page source
html_source = driver.page_source

# Load the page
driver.get("http://127.0.0.1:8050/prodeff")

# Wait for a certain time or until a specific condition is met
# Or use WebDriverWait for more precise waiting conditions

# Save the page source to a file
with open("pageofwcreport.html", "w", encoding='utf-8') as f:
    f.write(driver.page_source)

# Clean up
driver.quit()