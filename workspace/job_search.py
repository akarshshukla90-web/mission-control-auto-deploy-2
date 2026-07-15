import requests
import pandas as pd
from bs4 import BeautifulSoup
import selenium

def search_jobs(job_title, location):
    # Send GET request to the job search website
    url = f"https://www.example.com/search?q={job_title}&location={location}"
    response = requests.get(url)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the job listings from the page
    job_listings = soup.find_all('div', {'class': 'job-listing'})

    # Create a pandas DataFrame to store the job listings
    jobs = pd.DataFrame(columns=['Job Title', 'Company', 'Location', 'Salary'])

    # Loop through each job listing and extract the relevant information
    for job in job_listings:
        job_title = job.find('h2', {'class': 'job-title'}).text.strip()
        company = job.find('p', {'class': 'company'}).text.strip()
        location = job.find('p', {'class': 'location'}).text.strip()
        salary = job.find('p', {'class': 'salary'}).text.strip()

        # Append the job listing to the DataFrame
        jobs = jobs._append({'Job Title': job_title, 'Company': company, 'Location': location, 'Salary': salary}, ignore_index=True)

    return jobs

def main():
    job_title = input("Enter the job title: ")
    location = input("Enter the location: ")

    jobs = search_jobs(job_title, location)

    # Save the job listings to an Excel file
    jobs.to_excel(f"job_listings_{job_title}_{location}.xlsx", index=False)

if __name__ == "__main__":
    main()