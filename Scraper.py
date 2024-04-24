import re
import json
import mysql.connector
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import datetime

# Set Firefox options
options = Options()
options.headless = True  # You can comment/uncomment this line to toggle headless mode
options.set_preference("browser.userAgent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/100.0")
options.add_argument("--headless")

# Specify the path to the GeckoDriver executable
geckodriver_path = "SeleniumDriver/geckodriver"  # Replace with the actual path to geckodriver

# Initialize Firefox WebDriver
driver = webdriver.Firefox(options=options, service=Service(geckodriver_path))
driver.maximize_window()

# Open the file in read mode
with open("generated_url.txt", "r") as file:
    # Read the content of the file
    queryUrl = file.read().strip()

# Open indeed.com
driver.get(queryUrl)

# Get HTML content after page loads
html = driver.page_source

# Extract data and create a dictionary
data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
if data:
    data = json.loads(data[0])
else:
    raise Exception("No data found")

# Extract relevant attributes from the results
jobs = []

page = 0

while True:
    # Construct URL with page number
    url_with_page = f"{queryUrl}&start={page * 10}"  # Assuming 10 results per page
    
    # Open indeed.com
    driver.get(url_with_page)
    
    # Get HTML content after page loads
    html = driver.page_source
    
    # Extract data and create a dictionary
    data = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', html)
    if data:
        data = json.loads(data[0])
    else:
        break  # No more data found, exit the loop
    
    # Check if there are jobs available
    if "metaData" in data and "mosaicProviderJobCardsModel" in data["metaData"]:
        for job in data["metaData"]["mosaicProviderJobCardsModel"]["results"]:
            job_info = {
                "jobkey": job.get("jobkey", ""),
                "fetched": str(datetime.datetime.now()),
                "queryUrl": url_with_page,
                "viewJobLink": "https://www.indeed.com" + job.get("viewJobLink", ""),
                "link": "https://www.indeed.com" + job.get("link", ""),
                "normTitle": job.get("normTitle", ""),
                "title": job.get("title", ""),
                "displayTitle": job.get("displayTitle", ""),
                "company": job.get("company", ""),
                "encryptedFccompanyId": job.get("encryptedFccompanyId", "")
            }
            jobs.append(job_info)
    
    # Increment page number
    page += 1

# Close the browser
driver.quit()

# If there are no jobs, exit gracefully
if not jobs:
    print("No jobs found.")
    exit()

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

# Create tables if they do not exist
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Jobs (
        jobkey VARCHAR(255) PRIMARY KEY,
        fetched VARCHAR(255),
        queryUrl TEXT(500),
        viewJobLink TEXT(2500),
        link TEXT(2500),
        normTitle VARCHAR(255),
        title VARCHAR(255),
        displayTitle VARCHAR(255),
        company VARCHAR(255),
        encryptedFccompanyId VARCHAR(255)
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS tempJobs (
        jobkey VARCHAR(255) PRIMARY KEY,
        fetched VARCHAR(255),
        queryUrl TEXT(500),
        viewJobLink TEXT(2500),
        link TEXT(2500),
        normTitle VARCHAR(255),
        title VARCHAR(255),
        displayTitle VARCHAR(255),
        company VARCHAR(255),
        encryptedFccompanyId VARCHAR(255)
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        encryptedFccompanyId VARCHAR(64) PRIMARY KEY,
        Company VARCHAR(128)
    )
""")

# Insert data into the Jobs table, update if the jobkey already exists
for job in jobs:
    # Insert data into the Jobs table, update if the jobkey already exists
    columns = ', '.join(job.keys())
    placeholders = ', '.join(['%s'] * len(job))
    update_clause = ', '.join([f"{key} = VALUES({key})" for key in job.keys()])
    sql_job = f"INSERT INTO tempJobs (jobkey, fetched, queryUrl, viewJobLink, link, normTitle, title, displayTitle, company, \
        encryptedFccompanyId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                                    ON DUPLICATE KEY UPDATE \
                                        fetched = VALUE(fetched), \
                                        queryUrl = VALUE(queryUrl), \
                                        viewJobLink = VALUES(viewJobLink), \
                                        link = VALUES(link), \
                                        normTitle = VALUES(normTitle), \
                                        title = VALUES(title), \
                                        displayTitle = VALUES(displayTitle), \
                                        company = VALUES(company), \
                                        encryptedFccompanyId = VALUES(encryptedFccompanyId)"

    values_job = tuple(job.values())
    mycursor.execute(sql_job, values_job)

    # Insert data into the related tables
    jobkey = job['jobkey']
    
    mycursor.execute("""
        INSERT INTO Jobs 
        SELECT * FROM tempJobs
        WHERE jobkey NOT IN (SELECT jobkey FROM Jobs);
    """)
    mycursor.execute("""
        INSERT INTO companies 
        SELECT encryptedFccompanyId, Company FROM tempJobs
        WHERE encryptedFccompanyId NOT IN (SELECT encryptedFccompanyId FROM companies);
    """)
    
    mycursor.execute("""
        DELETE FROM tempJobs;
    """)

# Commit changes and close connection
mydb.commit()
mydb.close()

print("Job data saved to 'jobs.json' and inserted/updated into MySQL database.")
