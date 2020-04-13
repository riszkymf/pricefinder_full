import os,logging,datetime

from datetime import datetime,date

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from selenium.webdriver.remote.remote_connection import LOGGER

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

ES_INDEX_CONFIG_PATH = os.getenv("ES_INIT",os.path.join(ROOT_PATH,"es_index.yml"))
if not ES_INDEX_CONFIG_PATH:
    ES_INDEX_CONFIG_PATH = os.path.join(ROOT_PATH,"es_index.yml")
CONFIG_PATH = os.getenv("CONF_PATH",os.path.join(ROOT_PATH,"crawler/config"))

ES_HOST = os.getenv("ES_HANDLER","http://103.89.5.160:9200")
ES_USERNAME = os.getenv("ES_USERNAME","elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD","")
es = Elasticsearch(ES_HOST,http_auth=(ES_USERNAME,ES_PASSWORD))

__version__ = '0.0.0'

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

LOG_TYPE = os.environ.get('LOG_TYPE',"DEBUG")

now = datetime.now()
today = date.today().strftime('%Y-%m-%d')
filename = 'prc-crawler-%s.log' % (date.today().strftime('%Y-%m-%d',))
filepath = '/../log/' + filename
filepath = os.path.abspath(os.path.dirname(__file__))+filepath
LOGFILENAME = os.path.abspath(filepath)

if LOG_TYPE == "DEBUG":
    logging.basicConfig(level=logging.DEBUG, filename=LOGFILENAME, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
elif LOG_TYPE == "PRODUCTION":
    logging.basicConfig(level=logging.INFO, filename=LOGFILENAME, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

LOGGER.setLevel(logging.WARNING)
