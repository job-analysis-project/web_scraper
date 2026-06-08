from celery import Celery
from loguru import logger 
import pandas as pd

# read the connection settings for RabbitMQ, MySQL from config.py
from scraper.config import (
    MYSQL_ACCOUNT, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, RABBITMQ_HOST, RABBITMQ_PORT, WORKER_ACCOUNT, WORKER_PASSWORD
    )


# initialize the Celery app
app = Celery("task", 
             # the tasks to incude in this worker
             # only tasks that are defined using @app.task() decorator in the specified module will be registered with this Celery instance
             include=[
                 "scraper.tasks_104_scraper", # scraping 104
                 "scraper.tasks_cake_scraper" # scraping Cake
             ],

             broker=f"amqp://{WORKER_ACCOUNT}:{WORKER_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//")


# create the connection to MySQL database
engine = create_engine(
    f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/data_jobs"
)