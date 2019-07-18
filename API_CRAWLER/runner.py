from crawler.libs.run import *
from celery.schedules import crontab
from crawler.settings import *
from crawler.module.doombot import *
from crawler.libs.app import update_worker_status
import json
import requests

@celery_app.task(base=TaskErrorHandler)
def run_crawler():
    print("START CRAWLING PRICES")
    try:
        result=run(force_headless=False)
        register_data(result)
    except Exception as e:
        msg = "Fail during html checking : {}".format(e)
        update_worker_status(msg)

@celery_app.task(base=TaskErrorHandler)
def check_html_changes():
    print("CHECKING HTML CONTENT")
    try:
        res = content_check()
    except Exception as e:
        msg = "Fail during html checking : {}".format(e)
        update_worker_status(msg)

@celery_app.on_after_configure.connect
def setup_periodic_task(sender,**kwargs):
    sender.add_periodic_task(
        crontab(hour=PRICECRAWLER_CRONTAB_HOUR,day_of_week=PRICECRAWLER_CRONTAB_DAY_OF_WEEK)
        , run_crawler.s())
    sender.add_periodic_task(
        crontab(hour=HTML_CHECKER_CRONTAB_HOUR,day_of_week=HTML_CHECKER_CRONTAB_DAY_OF_WEEK),
        check_html_changes.s())

    # sender.add_periodic_task(
    #     10.0
    #     , run_crawler.s())
    # sender.add_periodic_task(
    #     15.0
    #     ,check_html_changes.s())

if __name__ == '__main__':
    celery_app.start()

