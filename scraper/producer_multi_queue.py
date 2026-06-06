from scraper.tasks_104_scraper import scrape_104_jobs
from scraper.tasks_cake_scraper import scrape_cake_jobs


# ------ 104 ------ #
task_104 = scrape_104_jobs.s("資料工程師", 1)
task_104.apply_async(queue="104_jobs") # send the task to the "104_jobs" queue 
print("Task for 104 scraper has been sent to the queue.")
# ------ Cake ------ #
task_cake = scrape_cake_jobs.s("data engineer")
task_cake.apply_async(queue="cake_jobs") # send the task to the "cake_jobs" queue
print("Task for Cake scraper has been sent to the queue.")