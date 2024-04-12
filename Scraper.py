import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

# Set Firefox options
options = Options()
options.headless = True  # You can comment/uncomment this line to toggle headless mode
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

# Extract relevant attributes from the results
jobs = []
for job in data["metaData"]["mosaicProviderJobCardsModel"]["results"]:
    job_info = {
        "title": job.get("title", ""),
        "searchUID": job.get("searchUID", ""),
        "truncatedCompany": job.get("truncatedCompany", ""),
        "jobLocationState": job.get("jobLocationState", ""),
        "jobLocationCity": job.get("jobLocationCity", ""),
        "company": job.get("company", ""),
        "extractedSalary": {
            "max": job.get("extractedSalary", {}).get("max", ""),
            "min": job.get("extractedSalary", {}).get("min", ""),
            "type": job.get("extractedSalary", {}).get("type", "")
        }   
    }
    jobs.append(job_info)

# Close the browser
driver.quit()

# Save job data to a JSON file
with open('jobs.json', 'w') as json_file:
    json.dump(jobs, json_file, indent=4)

# Print the path to the saved JSON data
print("Job data saved to 'jobs.json'")