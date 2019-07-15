import yaml
import json
from ..libs.util import *
from crawler.settings import *
from celery.schedules import crontab
from celery import Celery
import celery

class DoomConfig(object):

    def __init__(self,**kwargs):
        if kwargs:
            for key, value in kwargs.items():
                try:
                    setattr(self, key, value)
                except:
                    print("Can not set value")
                    pass

class DoomBot(celery.Task):
    config = None
    app = None

    def parse_config(self,config,bot_name="unnamed_worker"):
        self.app_name = bot_name
        d = {}
        for key,value in config.items():
            if key == 'schedule':
                d['schedule'] = flatten_dictionaries(value)
            elif key == 'retry':
                d['options'] = flatten_dictionaries(value)
            elif key == 'celery_config':
                d['celery_config'] = DoomConfig(**flatten_dictionaries(value))
        return d

    def build_celery(self):
        name = self.app_name
        app = Celery(name,broker=CELERY_BROKER)
        app.conf.timezone = CELERY_TIMEZONE
        if self.config['celery_config']:
            config = self.config['celery_config']
            app.config_from_object(config)
        return app

    
    def build_cron_schedule(self):
        app_name = self.app_name
        schedule = self.config['schedule']
        if schedule:
            val = crontab(**schedule)
        else:
            val = None
        d = {
            "task" : "task.add",
            "schedule" : val
        }
        d = {
            app_name : d
        }
        return d

    def send_doombot(self):
        pass

    def scheduling(self,sender):
        cron_schedule = self.build_cron_schedule

        return app


        


class TaskErrorHandler(celery.Task):
    endpoint = "/api/crawler"

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        data = {
            "status": "fail",
            "einfo": einfo
        }
    
    def on_success(retval, task_id, args, kwargs):
        data = {
            "status": "running",
            "einfo": "NONE"
        }
