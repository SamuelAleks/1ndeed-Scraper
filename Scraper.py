import re
import json
import html
import httpx
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


# Set Firefox options
options = Options()
# options.headless = True  # Uncomment this line if you want to run Firefox in headless mode
options.set_preference("browser.userAgent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/100.0")

# Specify the path to the GeckoDriver executable
geckodriver_path = "SeleniumDriver/geckodriver"  # Replace with the actual path to geckodriver

# Initialize Firefox WebDriver
driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)

# Open indeed.com
driver.get('https://www.indeed.com/jobs?q=programmer&l=Minnesota')

# Get HTML content after page loads
html = driver.page_source

# Extract data and create a dictionary
data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
data = json.loads(data[0])
print({
    "results": data["metaData"]["mosaicProviderJobCardsModel"]["results"],
    "meta": data["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"],
})

# Close the browser
driver.quit()

# Convert data to JSON format
json_data = json.dumps(data, indent=4)

# Save JSON data to a file
with open('data.json', 'w') as json_file:
    json_file.write(json_data)

# Print JSON data
print(json_data)
