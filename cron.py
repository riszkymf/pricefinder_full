import os,yaml,json

from crawler.libs.run import CrawlerExecutor as CE
from crawler.libs.handler import ESDataSend,generate_id
from crawler import logging

from elasticsearch import Elasticsearch
from elasticsearch import helpers

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

ES_INDEX_CONFIG_PATH = os.path.join(ROOT_PATH,"es_index.yml")
CONFIG_PATH = os.path.join(ROOT_PATH,"crawler/config")

ES_HOST = os.getenv("ES_HOST","http://103.89.5.160:9200")

ES_USERNAME = os.getenv("ES_USERNAME","elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD","")
es = Elasticsearch(ES_HOST,http_auth=(ES_USERNAME,ES_PASSWORD))

try:
    es.search(index="")
except Exception as e:
    print(str(e))
    logging.error("Failure to communicate with ElasticSearch")
    logging.error(str(e))
    raise


HEADLESS = os.getenv("HEADLESS",'0')
try:
    HEADLESS = bool(int(HEADLESS))
except ValueError :
    logging.ERROR("Headless Value must be either 0 or 1")
    HEADLESS = True

def send_data(es_handler, datasets):
    try:
        res = es_handler.search(index="domain_type")
        domain_type = [i["_source"]["type"] for i in res["hits"]["hits"]]
    except Exception :
        domain_type = ['.id', '.com', '.xyz', '.net', '.org', '.co.id', '.web.id', '.my.id', '.biz.id', '.ac.id', '.sch.id', '.biz', '.co', '.tv', '.io', '.info']
    result = list()
    for i in datasets:
        if i['_index'] == 'domain':
            if i['nm_domain_type'].lower() not in domain_type:
                continue
        try:
            res = es_handler.index(index=i.pop("_index"),id=i.pop("_id"),body=i)
        except Exception as e:
            logging.error(str(e))
            print(str(e))
            res = {"status": False}
        result.append(res)
    return result

## Load elasticsearch database configuration

with open(ES_INDEX_CONFIG_PATH,"r+") as f:
    data = f.read()
    es_init_indices = yaml.safe_load(data)


## Grab Configuration from Elasticsearch

res = es.search(index="crawler_config", body={"query": {"match_all": {}}})

conf_es = [json.loads(i["_source"]["config_json"]) for i in res["hits"]["hits"]]

## Configure DOOMBOT
_config = {
    "force_dump" : False,
    "stack_send": False
}

for crawler_configuration in conf_es:
    c = CE(json_config=crawler_configuration,force_headless=True,**_config)
    cfgs = c.crawler_configs
    result = list()
    config=c.scrape(cfgs)
    esdata = ESDataSend(es,es_init_indices,c.flattened_data)
    tmp = list()
    for i in esdata.rawdata:
        tmp.extend(esdata.compile_chunk_data(i))
    result = esdata.normalize(tmp)
    send_result = send_data(es,result)
    logging.debug(send_result)