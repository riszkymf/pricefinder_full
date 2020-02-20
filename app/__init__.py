import pymysql, logging, os

from app.libs.logger import create_logger

from datetime import datetime,date
from elasticsearch import Elasticsearch

from flask import Flask
from flask_cors import CORS

LOG_TYPE = os.environ.get('LOG_TYPE',"DEBUG")

now = datetime.now()
today = date.today().strftime('%Y-%m-%d')
filename = 'prcstats-%s.log' % (date.today().strftime('%Y-%m-%d',))
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

hosts = os.environ.get("ES_HOST","103.89.5.160:9200")
es = Elasticsearch(hosts=hosts)

database=os.environ.get("DB_NAME", os.getenv('DB_NAME'))
user=os.environ.get("DB_USER", os.getenv('DB_USER'))
password=os.environ.get("DB_PASSWORD", os.getenv('DB_PASSWORD'))
port=os.environ.get("DB_PORT", os.getenv('DB_PORT'))
host=os.environ.get("DB_HOST", os.getenv('DB_HOST'))


class HBConnection(object):

    def __init__(self):
        self.MYSQL_DATABASE_HOST=host
        self.MYSQL_DATABASE_PORT=port
        self.MYSQL_DATABASE_USER=user
        self.MYSQL_DATABASE_PASSWORD=password
        self.MYSQL_DATABASE_DB=database
        self.charset='utf8mb4'

    def start_connection(self):
        connection = pymysql.connect(
            host= self.MYSQL_DATABASE_HOST,
            user=self.MYSQL_DATABASE_USER,
            password=self.MYSQL_DATABASE_PASSWORD,
            db=self.MYSQL_DATABASE_DB,
            port=int(self.MYSQL_DATABASE_PORT),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)
        self.connection = connection
        return connection


APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def create_app():
    app = Flask(__name__)
    
    CORS(app)

    from .controllers import api_blueprint
    from .controllers import swaggerui_blueprint

    app.register_blueprint(swaggerui_blueprint, url_prefix=os.environ.get("/api/docs","/api/docs"))

    app.register_blueprint(api_blueprint)

    return app