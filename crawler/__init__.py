import os,logging,datetime

from datetime import datetime,date

from logger.loghandler import create_logger

from selenium.webdriver.remote.remote_connection import LOGGER

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
