from scraper.worker import app
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from loguru import logger 

@app.task()
# the scrape function for 104 jobs, takes in the search term and the page number as parameters
def scrape_104_jobs(search_term, page):
    based_url = "https://www.104.com.tw/jobs/search/api/jobs"

    # define the parameters for the GET request
    params = {
        "asc": 1,
        "jobsource": "joblist_search",
        "keyword": search_term,
        "mode": "s",
        "order": 4,
        "page": page,  # Inject the current page number
        "pagesize": 20,
        "searchJobs": 1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Referer": "https://www.104.com.tw/jobs/search/",
    }
    # for storing the results
    jobs = []
    # the acutal scraping process
    try:
        response = requests.get(based_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            data = data["data"]
            for job in data:
                description = {
                    "jobName": job["jobName"],
                    "company": job["custName"],
                    "location": job["jobAddrNoDesc"],
                    "experience": job["jobRo"],
                    "remote": job["remoteWorkType"],
                    "salary_low": job["salaryLow"],
                    "salary_high": job["salaryHigh"],
                    "link": job["link"]["job"],
                }
                jobs.append(description)
            df = pd.DataFrame(jobs)
            return df
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# ---------  testing code --------- #
# scrape_104_jobs('資料工程師', 1)
# print(scrape_104_jobs('資料工程師', 1))


# for printing out the results in the console
# the task is basically the same as scrape_104_jobs
@app.task()
def scrape_104_jobs_print(search_term, page):
    based_url = "https://www.104.com.tw/jobs/search/api/jobs"

    # define the parameters for the GET request
    params = {
        "asc": 1,
        "jobsource": "joblist_search",
        "keyword": search_term,
        "mode": "s",
        "order": 4,
        "page": page,  # Inject the current page number
        "pagesize": 20,
        "searchJobs": 1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Referer": "https://www.104.com.tw/jobs/search/",
    }
    # for storing the results
    jobs = []
    # the acutal scraping process
    try:
        response = requests.get(based_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            data = data["data"]
            for job in data:
                description = {
                    "source": "104",
                    "jobName": job["jobName"],
                    "company": job["custName"],
                    "location": job["jobAddrNoDesc"],
                    "experience": job["jobRo"],
                    "remote": job["remoteWorkType"],
                    "salary_low": job["salaryLow"],
                    "salary_high": job["salaryHigh"],
                    "link": job["link"]["job"],
                }
                jobs.append(description)
            print(jobs)
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# upload to MySQL in one task
@app.task()
def scrape_104_jobs_upload_mysql():
    from sqlalchemy import create_engine
    from sqlalchemy.dialects.mysql import insert
    from sqlalchemy import MetaData, Table, Column, String, Integer, Float, Date
    from scraper.config import MYSQL_ACCOUNT, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT
    
    df = scrape_104_jobs("資料工程師", 2)
    # create the connection to MySQL database
    engine = create_engine(
        f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/data_jobs"
    )

    metadata = MetaData()
    # go through the dataframe and insert each row into the MySQL database
    for _, row in df.iterrows():
        # create an insert statement for the job listing
        stmt = insert(Table("jobs_104", MetaData(), autoload_with=engine)).values(
            job_name=row["jobName"],
            company=row["company"],
            location=row["location"],
            experience=row["experience"],
            remote=row["remote"],
            salary_low=row["salary_low"],
            salary_high=row["salary_high"],
            link=row["link"],
        )
        # execute the insert statement
        with engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()  # commit the transaction after each insert
        logger.info(f"Finished uploading job: {row['jobName']} at {row['company']} to MySQL database.")
