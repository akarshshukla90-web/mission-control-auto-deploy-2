import urllib.request
import json
import time

url = "http://localhost:8000/api/broadcast"
data = {
    "title": "Job Search Automation",
    "message": "build an automation that runs and searches for job (INDIA and International) (both remote and onsite in Vadodara, Pune, Delhi, and Mumbai) with a minimum package of 6 lakh LPA related to my resume, tailors my resume and cover letter to each job description, applies to them, creates logins for new websites, and saves everything in an Excel file on my desktop with a timestamp"
}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    print(response.read().decode())
    
print("Task broadcasted. Check Mission Control dashboard or the server console for activity!")
