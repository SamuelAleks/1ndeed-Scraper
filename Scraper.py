import re
import json
import mysql.connector
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
driver = webdriver.Firefox(options=options, service=Service(geckodriver_path))

# Open indeed.com
driver.get('https://www.indeed.com/jobs?q=programmer')

# Get HTML content after page loads
html = driver.page_source

# Extract data and create a dictionary
data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
data = json.loads(data[0])

# Extract relevant attributes from the results
jobs = []
for job in data["metaData"]["mosaicProviderJobCardsModel"]["results"]:
    job_info = {
        "jobkey": job.get("jobkey", ""),
        "title": job.get("title", ""),
        "searchUID": job.get("searchUID", ""),
        "truncatedCompany": job.get("truncatedCompany", ""),
        "jobLocationState": job.get("jobLocationState", ""),
        "jobLocationCity": job.get("jobLocationCity", ""),
        "company": job.get("company", ""),
        "extractedSalary_max": job.get("extractedSalary", {}).get("max", ""),  # Flatten extractedSalary
        "extractedSalary_min": job.get("extractedSalary", {}).get("min", ""),
        "extractedSalary_type": job.get("extractedSalary", {}).get("type", "")
    }
    jobs.append(job_info)

# Close the browser
driver.quit()

# Save job data to a JSON file
with open('jobs.json', 'w') as json_file:
    json.dump(jobs, json_file, indent=4)

# Connect to MySQL Database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="test"
)

# Create a cursor object
mycursor = mydb.cursor()

# Create jobs table if not exists
mycursor.execute("CREATE TABLE IF NOT EXISTS jobs (jobkey VARCHAR(255) PRIMARY KEY, title VARCHAR(255), searchUID VARCHAR(255), truncatedCompany VARCHAR(255), jobLocationState VARCHAR(255), jobLocationCity VARCHAR(255), company VARCHAR(255), extractedSalary_max VARCHAR(255), extractedSalary_min VARCHAR(255), extractedSalary_type VARCHAR(255))")

# Insert data into the jobs table, update if the jobkey already exists
for job in jobs:
    columns = ', '.join(job.keys())
    placeholders = ', '.join(['%s'] * len(job))
    update_clause = ', '.join([f"{key} = VALUES({key})" for key in job.keys()])
    sql = f"INSERT INTO jobs ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"
    values = tuple(job.values())
    mycursor.execute(sql, values)

# Commit changes and close connection
mydb.commit()
mydb.close()

print("Job data saved to 'jobs.json' and inserted/updated into MySQL database.")
