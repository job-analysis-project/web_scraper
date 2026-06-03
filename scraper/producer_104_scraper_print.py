# this file is only for testsing sending multiple tasks to the broker, and to test the functionality of the scraper
from scraper.tasks_104_scraper import scrape_104_jobs_print

for args in [('資料工程師', 1), ('資料分析師', 1), ('軟體工程師', 1)]:
    print(f'Looking for role {args[0]}')
    scrape_104_jobs_print.delay(*args)