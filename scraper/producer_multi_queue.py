from scraper.tasks_104_scraper import scrape_104_jobs_upload_mysql
from scraper.tasks_cake_scraper import scrape_cake_jobs


# ------ 104 ------ #

# # the roles to look for and the page number to scrape
# search_keyword, page = "資料工程師", 1

# # send the task to the "104_jobs" queue
# task_104 = scrape_104_jobs.s(search_keyword, page)
# task_104.apply_async(queue="104_jobs") # send the task to the "104_jobs" queue 
# print("Task for 104 scraper has been sent to the queue.")

# ------ 104 ------ loop ver. #
# start page and end page
start = 1
end = 6

for page_num in range(start, end + 1):
    args = ('資料工程師', page_num)
    task_104 = scrape_104_jobs_upload_mysql.s(*args)
    task_104.apply_async(queue='104_jobs') # send the task to the '104_jobs' queue
print(f'{end} tasks for 104 scraper sent to the queue!')



# ------ Cake ------ #

# the roles to look for on cake
search_keyword = "data engineer"

# send the task to the "cake_jobs" queue
task_cake = scrape_cake_jobs.s(search_keyword)
task_cake.apply_async(queue="cake_jobs") # send the task to the "cake_jobs" queue
print("Task for Cake scraper has been sent to the queue.")