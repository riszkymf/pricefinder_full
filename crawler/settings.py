from dotenv import load_dotenv
import os

HOME = os.path.expanduser('~')

load_dotenv(verbose=True)
cwd = os.getcwd()
other_env = os.path.abspath("{}/../.env".format(cwd))
load_dotenv(dotenv_path=other_env)

## CRAWLER CONFIGURATION FOLDERs
CONF_PATH = os.getenv("CRAWLER_CONFIGURATION_PATH")
DUMP_LOCATION = os.getenv("DATA_DUMP_LOCATION")
SEND_STATUS = os.getenv("SEND_STATUS_LOC")
HTML_LOCATION = os.getenv("HTML_CONTENT_DUMP_LOCATION")
TEST_PATH = os.getenv("CRAWLER_CONFIGURATION_PATH")
APP_URL = os.getenv("CRAWLER_URL")



## CRAWLER CONFIG
ID_WORKER = os.getenv("ID_WORKER")
LOC_SCHEDULE_CONFIG = os.getenv("LOC_SCHEDULE_CONFIG")
LOC_CONFIG = os.getenv("LOC_CONFIG")