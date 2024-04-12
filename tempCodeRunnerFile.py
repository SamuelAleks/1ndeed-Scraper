import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

# Set Firefox options
options = Options()
# options.headless = True  # Uncomment this line if you want to run Firefox in headless mode
options.set_preference("browser.userAgent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/100.0")

# Specify the path to the GeckoDriver executable
geckodriver_path = "/usr/bin/geckodriver"  # Replace with the actual path to geckodriver

# Initialize Firefox WebDriver
driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)

# Open indeed.com
driver.get('https://www.indeed.com/jobs?q=programmer&l=Minnesota&vjk=6b02886d0966dca2')

# You can add more actions here, like searching for jobs or interacting with the website.

# Extract data and create a dictionary
data = {
    "url": driver.current_url,
    # Add more data as needed
}

# Close the browser
driver.quit()

# Convert data to JSON format
json_data = json.dumps(data, indent=4)

# Save JSON data to a file
with open('data.json', 'w') as json_file:
    json_file.write(json_data)

# Print JSON data
print(json_data)
