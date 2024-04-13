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
driver.get('https://www.indeed.com/jobs?q=programmer&l=minnesota')

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
        "viewJobLink": job.get("viewJobLink", ""),
        "link": job.get("link", ""),
        "normTitle": job.get("normTitle", ""),
        "title": job.get("title", ""),
        "displayTitle": job.get("displayTitle", ""),
        "company": job.get("company", ""),
        "truncatedCompany": job.get("truncatedCompany", ""),
        "companyBrandingAttributes": {
            "headerImageUrl": job.get("companyBrandingAttributes", {}).get("headerImageUrl", ""),
            "logoUrl": job.get("companyBrandingAttributes", {}).get("logoUrl", "")
        },
        "thirdPartyApplyUrl": job.get("thirdPartyApplyUrl", ""),
        "companyRating": job.get("companyRating", 0),
        "companyReviewCount": job.get("companyReviewCount", 0),
        "featuredEmployer": job.get("featuredEmployer", False),
        "featuredEmployerCandidate": job.get("featuredEmployerCandidate", False),
        "feedId": job.get("feedId", 0),
        "formattedActivityDate": job.get("formattedActivityDate", ""),
        "formattedLocation": job.get("formattedLocation", ""),
        "formattedRelativeTime": job.get("formattedRelativeTime", ""),
        "jobLocationState": job.get("jobLocationState", ""),
        "jobLocationCity": job.get("jobLocationCity", ""),
        "extractedSalary_max": max(job.get("extractedSalary", {}).get("max", 0), 0),
        "extractedSalary_min": max(job.get("extractedSalary", {}).get("min", 0), 0),
        "extractedSalary_type": job.get("extractedSalary", {}).get("type", ""),
        #"enhancedAttributesModel": job.get("enhancedAttributesModel", {}),
        #"hiringMultipleCandidatesModel": job.get("hiringMultipleCandidatesModel", {}),
        #"jobTypes": job.get("jobTypes", []),
        #"openInterviewsInterviewsOnTheSpot": job.get("openInterviewsInterviewsOnTheSpot", False),
        "openInterviewsJob": job.get("openInterviewsJob", False),
        "openInterviewsOffersOnTheSpot": job.get("openInterviewsOffersOnTheSpot", False),
        "openInterviewsPhoneJob": job.get("openInterviewsPhoneJob", False),
        "remoteLocation": job.get("remoteLocation", False),
        #"remoteWorkModel": job.get("remoteWorkModel", {}),
        #"salarySnippet": job.get("salarySnippet", {}),
        "sourceId": job.get("sourceId", 0),
        "sponsored": job.get("sponsored", False),
        #"taxonomyAttributes": job.get("taxonomyAttributes", []),
        "createDate": job.get("createDate", 0),
        "pubDate": job.get("pubDate", 0),
        "expired": job.get("expired", False),
        "searchUID": job.get("searchUID", "")
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

mycursor.execute("""
                 DROP TABLE IF EXISTS TaxonomyAttributes;
                 DROP TABLE IF EXISTS SalarySnippet;
                 DROP TABLE IF EXISTS RemoteWorkModel;
                 DROP TABLE IF EXISTS HiringMultipleCandidatesModel;
                 DROP TABLE IF EXISTS EnhancedAttributesModel;
                 DROP TABLE IF EXISTS CompanyBrandingAttributes;
                 
                 DROP TABLE IF EXISTS Jobs;
                 
                 """, multi=True)

# Create tables if they do not exist
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS Jobs (
        jobkey VARCHAR(255) PRIMARY KEY,
        viewJobLink TEXT(2500),
        link TEXT(2500),
        normTitle VARCHAR(255),
        title VARCHAR(255),
        displayTitle VARCHAR(255),
        company VARCHAR(255),
        truncatedCompany VARCHAR(255),
        thirdPartyApplyUrl TEXT(2500),
        companyRating DECIMAL(3, 1),
        companyReviewCount INT,
        featuredEmployer BOOLEAN,
        featuredEmployerCandidate BOOLEAN,
        feedId INT,
        formattedActivityDate VARCHAR(50),
        formattedLocation VARCHAR(255),
        formattedRelativeTime VARCHAR(50),
        jobLocationState VARCHAR(2),
        jobLocationCity VARCHAR(255),
        extractedSalary_max DECIMAL(12, 2),
        extractedSalary_min DECIMAL(12, 2),
        extractedSalary_type VARCHAR(50),
        openInterviewsInterviewsOnTheSpot BOOLEAN,
        openInterviewsJob BOOLEAN,
        openInterviewsOffersOnTheSpot BOOLEAN,
        openInterviewsPhoneJob BOOLEAN,
        remoteLocation BOOLEAN,
        sourceId INT, -- Add this column
        sponsored BOOLEAN DEFAULT FALSE,
        createDate VARCHAR(255),
        pubDate VARCHAR(255),
        expired BOOLEAN DEFAULT 0,
        searchUID VARCHAR(255)
    )

""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS CompanyBrandingAttributes (
        jobkey VARCHAR(255) PRIMARY KEY,
        headerImageUrl VARCHAR(255),
        logoUrl VARCHAR(255),
        FOREIGN KEY (jobkey) REFERENCES Jobs(jobkey) ON DELETE CASCADE
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS EnhancedAttributesModel (
        jobkey VARCHAR(255) PRIMARY KEY,
        displayType VARCHAR(50),
        maximumHours INT,
        minimumHours INT,
        period VARCHAR(50),
        source VARCHAR(50),
        FOREIGN KEY (jobkey) REFERENCES Jobs(jobkey) ON DELETE CASCADE
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS HiringMultipleCandidatesModel (
        jobkey VARCHAR(255) PRIMARY KEY,
        hiresNeeded VARCHAR(50),
        hiresNeededExact VARCHAR(50),
        FOREIGN KEY (jobkey) REFERENCES Jobs(jobkey) ON DELETE CASCADE
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS RemoteWorkModel (
        jobkey VARCHAR(255) PRIMARY KEY,
        inlineText BOOLEAN,
        text VARCHAR(50),
        type VARCHAR(50),
        FOREIGN KEY (jobkey) REFERENCES Jobs(jobkey) ON DELETE CASCADE
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS SalarySnippet (
        jobkey VARCHAR(255) PRIMARY KEY,
        currency VARCHAR(3),
        salaryTextFormatted BOOLEAN,
        source VARCHAR(50),
        text VARCHAR(255),
        FOREIGN KEY (jobkey) REFERENCES Jobs(jobkey) ON DELETE CASCADE
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS TaxonomyAttributes (
        jobkey VARCHAR(255),
        attributeLabel VARCHAR(50),
        attributeValue VARCHAR(255),
        PRIMARY KEY (jobkey, attributeLabel),
        FOREIGN KEY (jobkey) REFERENCES Jobs(jobkey) ON DELETE CASCADE
    )
""")

# Insert data into the Jobs table, update if the jobkey already exists
for job in jobs:
    # Insert data into the Jobs table, update if the jobkey already exists
    columns = ', '.join(job.keys())
    placeholders = ', '.join(['%s'] * len(job))
    update_clause = ', '.join([f"{key} = VALUES({key})" for key in job.keys()])
    sql_job = f"INSERT INTO Jobs (jobkey, viewJobLink, link, normTitle, title, displayTitle, company, \
            truncatedCompany, thirdPartyApplyUrl, companyRating, companyReviewCount, featuredEmployer, featuredEmployerCandidate, \
                    feedId, formattedActivityDate, formattedLocation, formattedRelativeTime, jobLocationState, \
                        jobLocationCity, extractedSalary_max, extractedSalary_min, extractedSalary_type, openInterviewsJob, \
                            openInterviewsOffersOnTheSpot, openInterviewsPhoneJob, remoteLocation, sourceId, sponsored, \
                                createDate, pubDate, expired, searchUID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                                        ON DUPLICATE KEY UPDATE \
                                            viewJobLink = VALUES(viewJobLink), \
                                            link = VALUES(link), \
                                            normTitle = VALUES(normTitle), \
                                            title = VALUES(title), \
                                            displayTitle = VALUES(displayTitle), \
                                            company = VALUES(company), \
                                            truncatedCompany = VALUES(truncatedCompany), \
                                            thirdPartyApplyUrl = VALUES(thirdPartyApplyUrl), \
                                            companyRating = VALUES(companyRating), \
                                            companyReviewCount = VALUES(companyReviewCount), \
                                            featuredEmployer = VALUES(featuredEmployer), \
                                            featuredEmployerCandidate = VALUES(featuredEmployerCandidate), \
                                            feedId = VALUES(feedId), \
                                            formattedActivityDate = VALUES(formattedActivityDate), \
                                            formattedLocation = VALUES(formattedLocation), \
                                            formattedRelativeTime = VALUES(formattedRelativeTime), \
                                            jobLocationState = VALUES(jobLocationState), \
                                            jobLocationCity = VALUES(jobLocationCity), \
                                            extractedSalary_max = VALUES(extractedSalary_max), \
                                            extractedSalary_min = VALUES(extractedSalary_min), \
                                            extractedSalary_type = VALUES(extractedSalary_type), \
                                            openInterviewsJob = VALUES(openInterviewsJob), \
                                            openInterviewsOffersOnTheSpot = VALUES(openInterviewsOffersOnTheSpot), \
                                            openInterviewsPhoneJob = VALUES(openInterviewsPhoneJob), \
                                            remoteLocation = VALUES(remoteLocation), \
                                            sourceId = VALUES(sourceId), \
                                            sponsored = VALUES(sponsored), \
                                            createDate = VALUES(createDate), \
                                            pubDate = VALUES(pubDate), \
                                            expired = VALUES(expired), \
                                            searchUID = VALUES(searchUID)"

    values_job = tuple(job.values())
    mycursor.execute(sql_job, values_job)

    # Insert data into the related tables
    jobkey = job['jobkey']
'''
    # CompanyBrandingAttributes
    branding_attributes = job['companyBrandingAttributes']
    if branding_attributes:
        header_image_url = branding_attributes.get('headerImageUrl', '')
        logo_url = branding_attributes.get('logoUrl', '')
        sql_branding = "INSERT INTO CompanyBrandingAttributes (jobkey, headerImageUrl, logoUrl) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE headerImageUrl = VALUES(headerImageUrl), logoUrl = VALUES(logoUrl)"
        values_branding = (jobkey, header_image_url, logo_url)
        mycursor.execute(sql_branding, values_branding)

    # EnhancedAttributesModel
    enhanced_attributes = job['enhancedAttributesModel']
    if enhanced_attributes:
        display_type = enhanced_attributes.get('displayType', '')
        maximum_hours = enhanced_attributes.get('maximumHours', 0)
        minimum_hours = enhanced_attributes.get('minimumHours', 0)
        period = enhanced_attributes.get('period', '')
        source = enhanced_attributes.get('source', '')
        sql_enhanced = "INSERT INTO EnhancedAttributesModel (jobkey, displayType, maximumHours, minimumHours, period, source) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE displayType = VALUES(displayType), maximumHours = VALUES(maximumHours), minimumHours = VALUES(minimumHours), period = VALUES(period), source = VALUES(source)"
        values_enhanced = (jobkey, display_type, maximum_hours, minimum_hours, period, source)
        mycursor.execute(sql_enhanced, values_enhanced)
        
    # Insert data into the related tables

    # HiringMultipleCandidatesModel
    hiring_multiple_candidates = job['hiringMultipleCandidatesModel']
    if hiring_multiple_candidates:
        hires_needed = hiring_multiple_candidates.get('hiresNeeded', '')
        hires_needed_exact = hiring_multiple_candidates.get('hiresNeededExact', '')
        sql_hiring = "INSERT INTO HiringMultipleCandidatesModel (jobkey, hiresNeeded, hiresNeededExact) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE hiresNeeded = VALUES(hiresNeeded), hiresNeededExact = VALUES(hiresNeededExact)"
        values_hiring = (jobkey, hires_needed, hires_needed_exact)
        mycursor.execute(sql_hiring, values_hiring)

    # RemoteWorkModel
    remote_work = job['remoteWorkModel']
    if remote_work:
        inline_text = remote_work.get('inlineText', False)
        text = remote_work.get('text', '')
        r_type = remote_work.get('type', '')
        sql_remote = "INSERT INTO RemoteWorkModel (jobkey, inlineText, text, type) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE inlineText = VALUES(inlineText), text = VALUES(text), type = VALUES(type)"
        values_remote = (jobkey, inline_text, text, r_type)
        mycursor.execute(sql_remote, values_remote)

    # SalarySnippet
    salary_snippet = job['salarySnippet']
    if salary_snippet:
        currency = salary_snippet.get('currency', '')
        salary_text_formatted = salary_snippet.get('salaryTextFormatted', False)
        source = salary_snippet.get('source', '')
        salary_text = salary_snippet.get('text', '')
        sql_salary = "INSERT INTO SalarySnippet (jobkey, currency, salaryTextFormatted, source, text) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE currency = VALUES(currency), salaryTextFormatted = VALUES(salaryTextFormatted), source = VALUES(source), text = VALUES(text)"
        values_salary = (jobkey, currency, salary_text_formatted, source, salary_text)
        mycursor.execute(sql_salary, values_salary)

    # TaxonomyAttributes
    taxonomy_attributes = job['taxonomyAttributes']
    for attribute in taxonomy_attributes:
        attribute_label = attribute.get('attributeLabel', '')
        attribute_value = attribute.get('attributeValue', '')
        sql_taxonomy = "INSERT INTO TaxonomyAttributes (jobkey, attributeLabel, attributeValue) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE attributeLabel = VALUES(attributeLabel), attributeValue = VALUES(attributeValue)"
        values_taxonomy = (jobkey, attribute_label, attribute_value)
        mycursor.execute(sql_taxonomy, values_taxonomy)
'''

# Commit changes and close connection
mydb.commit()
mydb.close()

print("Job data saved to 'jobs.json' and inserted/updated into MySQL database.")
