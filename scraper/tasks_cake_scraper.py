from scraper.worker import app
import requests
from bs4 import BeautifulSoup
import re 
import pandas as pd
from loguru import logger 
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.pool import NullPool
from sqlalchemy import MetaData, Table, Column, Integer, String, CHAR, Text, TIMESTAMP, UniqueConstraint, text
from scraper.config import MYSQL_ACCOUNT, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT
        

CAKE_JOB_URL = "https://www.cake.me/jobs"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

# create the connection to MySQL database
# engine = create_engine(
#     f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/data_jobs",
#     poolclass=NullPool
# )
# # define the table 
# metadata = MetaData()

# jobs_table = Table(
#     "jobs_cake", 
#     metadata,
#     Column("id", Integer, primary_key=True, autoincrement=True),
#     Column("job_name", String(100), nullable=False),
#     Column("company", String(50), nullable=False),
#     Column("location", String(50), nullable=False),
#     Column("experience", Integer, nullable=False),
#     Column("remote", CHAR(3), nullable=False),
#     Column("salary_low", Integer, nullable=False),
#     Column("salary_high", Integer, nullable=False),
#     Column("link", Text, nullable=False),
#     Column("inserted_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    
#     # unique key to prevent duplicated job postings
#     UniqueConstraint("job_name", "company", "location", name="uix_job_company_location")
# )


# the main function to scrape job listings from Cake's job board based on the search term
@app.task()
def scrape_cake_jobs(search_terms):

    # covert space to `%20` for url encoding
    encoded_terms = search_terms.replace(" ", "%20")
    search_url = f"{CAKE_JOB_URL}/{encoded_terms}"

    # send a GET request to the search URL
    parsed_jobs = []
    try:
        response = requests.get(search_url, headers=DEFAULT_HEADERS, timeout=10)
        if  response.status_code != 200:
            print(f"Failed to access the website. Status code: {response.status_code}")

            return []
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred:{e}")
        return []
    # empty list to store the parsed job features
    parsed_jobs = []

    # extracting data from soup object
    # find all job listings on the page
    job_listings = soup.find_all("div", class_="JobSearchItem-module-scss-module___szW4W__container")
    
    # the features blocks for each job listing
    features_lst = soup.find_all("div", class_="JobSearchItem-module-scss-module___szW4W__features")
    
    for job_listing, features in zip(job_listings, features_lst):

        # extract title and company name
        title, company = job_listing.find('a', class_="JobSearchItem-module-scss-module___szW4W__jobTitle"),\
                         job_listing.find('a', class_="JobSearchItem-module-scss-module___szW4W__companyName")
        
        # fetch the link to the job posting
        if title['href']:
            link = title['href']
        else:
            link = None
        
        title = title.get_text(strip=True)
        company = company.get_text(strip=True)

        # initialize an empty list to store the features
        job_feature = {
            "job_name": title,
            # "job_name": job.get_text(strip=True),
            "company": company,
            "location": None,
            "seniority": None,
            "remote": None,
            "salary": None,
            "experience": None,
            "management_resp": None,
            "job_type": None,
            "link": link
        }

        # extract the features for each job listing
        rows = features.find_all("div", class_=re.compile("inlineMessage"))
        for row in rows:
            # identify the icon tag
            icon_tag = row.find("i", class_="fa")
            if not icon_tag:
                continue
            classes = icon_tag.get("class", [])

            label_div = row.find("div", class_=re.compile("__label"))
            if not label_div:
                continue

            # logic to determine the feature type based on the icon class
            if any("fa-user" in cls for cls in classes):
                links = label_div.find_all("a")
                if len(links) >= 1:
                    job_feature["job_type"] = links[0].get_text(strip=True)
                if len(links) >= 2:
                    job_feature["seniority"] = links[1].get_text(strip=True)
            
            elif any("fa-map-marker" in cls for cls in classes):
                locations = [a.get_text(strip=True) for a in label_div.find_all("a")]
                job_feature["location"] = ", ".join(locations) if locations else label_div.get_text(strip=True)
            
            elif any("fa-dollar-sign" in cls for cls in classes):
                job_feature["salary"] = label_div.get_text(strip=True) 

            elif any("fa-business-time" in cls for cls in classes):
                job_feature["experience"] = label_div.get_text(strip=True)

            elif any("fa-sitemap" in cls for cls in classes):
                job_feature["management_resp"] = label_div.get_text(strip=True)
            
        parsed_jobs.append(job_feature)
        df = pd.DataFrame(parsed_jobs)

    return df
    # df.to_csv('./cake_test.csv', mode='w')
    # # print(df['company'])
    # # print(df)
    # # print(df.columns)