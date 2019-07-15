from crawler.libs.run import *
from celery.schedules import crontab
from crawler.settings import CRONTAB_DAY_OF_WEEK,CRONTAB_HOUR,CRONTAB_MINUTE
import json
import requests

@celery_app.task
def run_crawler():
    # result=run(force_headless=False)
    # register_data(result)
    requests.get('http://127.0.0.1:6968/api/company')

@celery_app.on_after_configure.connect
def setup_periodic_task(sender,**kwargs):
    sender.add_periodic_task(
        5.0
        , run_crawler.s())

if __name__ == '__main__':
    celery_app.start()

