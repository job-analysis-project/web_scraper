from scraper.tasks_cake_scraper import scrape_cake_jobs
from scraper.tasks_104_scraper import scrape_104_jobs
from scraper.tasks_104_scraper import scrape_104_jobs_upload_mysql

# scrape_cake_jobs.delay('資料工程師')
scrape_104_jobs.delay('資料工程師', 2)
scrape_104_jobs_upload_mysql.delay()