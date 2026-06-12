# this is a test file to test the connection between producer and consumer, and to test the functionality of the scraper
# the corresponding consumer is the Celery worker in worker.py
# the worker flow: producer.py -> RabbitMQ (queue) -> worker.py (Celery worker) -> scrape_104_jobs.py (scraper function)
from scraper.tasks_104_scraper import scrape_104_jobs

# distribute the task to the Celery worker, and get the result

# start page & end page
start = 1
end = 5

for page_num in range(start, end):

    args = ('資料工程師', page_num)  # example arguments for the scraping task
    print(f"Loading page {page_num}...")
    scrape_104_jobs.delay(*args)  # use .delay() to send the task to the Celery worker asynchronously