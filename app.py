from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pymysql
import time
from urllib.parse import quote
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
import time

app = Flask(__name__)
CORS(app)

# Function to fetch data from MySQL database
def fetch_data_from_database():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 database='test',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Jobs")
            data = cursor.fetchall()
            return data
    finally:
        connection.close()

# Function to call Scraper.py
def call_scraper():
    subprocess.call(["python", "Scraper.py"])

# Schedule Scraper.py to be called every minute
# schedule.every(10).minutes.do(call_scraper)

sched = BackgroundScheduler(daemon=True)
sched.add_job(call_scraper,'interval',minutes=30)
sched.start()


@app.route('/scrape-data', methods=['GET', 'POST'])
def scrape():
    try:
        call_scraper()
        return jsonify({"message": "Scraping initiated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error initiating scraping", "error": str(e)}), 500

# Route to fetch data from database every 10 seconds
@app.route('/fetch-data')
def fetch_data():
    data = fetch_data_from_database()
    return jsonify(data)

# Route to manually fetch data
@app.route('/manual-fetch', methods=['POST'])
def manual_fetch():
    data = fetch_data_from_database()
    return jsonify(data)

# Route to serve the frontend
@app.route('/')
def index():
    return render_template('jobs.html')

@app.route('/url-builder', methods=['GET','POST'])
def generate_url():
    # Get the form data
    location = request.form.get('location')
    query = request.form.get('query')
    date_posted = request.form.get('date_posted')
    remote = request.form.get('remote')
    salary = request.form.get('salary')
    job_type = request.form.get('job_type')
    encourage_to_apply = request.form.get('encourage_to_apply')
    company = request.form.get('company')

    # Build the URL
    url = "https://indeed.com/jobs?"

    if query and salary:
        url += f"q={quote(query + ' $' + salary)}&"
    elif query:
        url += f"q={quote(query)}&"

    if location:
        url += f"l={quote(location)}&"

    if date_posted:
        url += f"fromage={quote(date_posted)}&"

    sc = []
    if remote == "yes":
        sc.append("attr(DSQF7)")
    if job_type:
        sc.append(f"jt({quote(job_type)})")
    if encourage_to_apply == "No Degree":
        sc.append("attr(JPSJ9)")
    if company:
        sc.append(f"fcckey({quote(company)})")

    if sc:
        url += f"sc=0kf%3A{''.join(sc)}%3B"

    # Save the URL to a text file
    with open('generated_url.txt', 'w') as f:
        f.write(url)

    return render_template('url_builder.html', url=url)

if __name__ == '__main__':
    app.run(debug=True)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
