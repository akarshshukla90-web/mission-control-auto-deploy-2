import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def apply_jobs(jobs):
    # Create a new instance of the Chrome driver
    driver = selenium.Chrome()

    # Loop through each job listing and apply to the job
    for index, row in jobs.iterrows():
        # Open the job listing page
        driver.get(row['Job Title'])

        # Wait for the job title to be visible
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//h2[@class='job-title']")))

        # Extract the job title from the page
        job_title = driver.find_element(By.XPATH, "//h2[@class='job-title']").text

        # Enter the job title in the job title field
        job_title_field = driver.find_element(By.XPATH, "//input[@id='job_title']")
        job_title_field.send_keys(job_title)

        # Enter the company name in the company field
        company_field = driver.find_element(By.XPATH, "//input[@id='company']")
        company_field.send_keys(row['Company'])

        # Enter the location in the location field
        location_field = driver.find_element(By.XPATH, "//input[@id='location']")
        location_field.send_keys(row['Location'])

        # Enter the salary in the salary field
        salary_field = driver.find_element(By.XPATH, "//input[@id='salary']")
        salary_field.send_keys(row['Salary'])

        # Submit the form
        submit_button = driver.find_element(By.XPATH, "//button[@id='submit']")
        submit_button.click()

        # Wait for the form to be submitted
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.XPATH, "//button[@id='submit']")))

        # Close the browser window
        driver.quit()

if __name__ == "__main__":
    jobs = pd.read_excel("job_listings.xlsx")
    apply_jobs(jobs)