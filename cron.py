import os,yaml

from crawler.libs.run import CrawlerExecutor as CE
from crawler.libs.handler import ESDataSend,generate_id
from crawler import logging

from elasticsearch import Elasticsearch
from elasticsearch import helpers

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

ES_INDEX_CONFIG_PATH = os.path.join(ROOT_PATH,"es_index.yml")
CONFIG_PATH = os.path.join(ROOT_PATH,"crawler/config")

ES_HOST = os.getenv("ES_HANDLER","http://103.89.5.160:9200")

es = Elasticsearch(ES_HOST)

HEADLESS = os.getenv("HEADLESS",'0')
try:
    HEADLESS = bool(int(HEADLESS))
except ValueError :
    logging.ERROR("Headless Value must be either 0 or 1")
    HEADLESS = True

crawler = CE(path=CONFIG_PATH,force_headless=HEADLESS)
crawler_config = crawler.crawler_configs
result = list()

for n,i in enumerate(crawler_config):
    config=crawler.scrape(i['crawler_configuration'])
    result.append(crawler.flattened_data)

with open(ES_INDEX_CONFIG_PATH,"r+") as f:
    data = f.read()
    es_init_indices = yaml.safe_load(data)

esdata = ESDataSend(es,es_init_indices,crawler.flattened_data)
tmp = list()
for i in esdata.rawdata:
    tmp.extend(esdata.compile_chunk_data(i))
result = esdata.normalize(tmp)

