import os
import json
import yaml
from pathlib import Path
from crawler.libs.handler import ESDataSend,generate_id
from crawler.libs.util import dump_to_tmp,load_config
from crawler import logging


from elasticsearch import Elasticsearch
from elasticsearch import helpers

ROOT_PATH = Path(__file__).parent
TMP_PATH = os.path.join(ROOT_PATH,"tmp")
ES_INDEX_CONFIG_PATH = os.path.join(ROOT_PATH,"es_index.yml")
CONFIG_PATH = os.path.join(ROOT_PATH,"crawler/config")

ES_HOST = os.getenv("ES_HOST","http://10.10.3.45:9200")
ES_USERNAME = os.getenv("ES_USERNAME","elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD","BiznetGio2017")
es = Elasticsearch(ES_HOST,http_auth=(ES_USERNAME,ES_PASSWORD))


with open(ES_INDEX_CONFIG_PATH,"r+") as f:
    data = f.read()
    es_init_indices = yaml.safe_load(data)

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

result_files = list()
read_result = list()
for f in os.listdir(TMP_PATH):
    f_name = f.split("/")[-1]
    if f_name.startswith("rslt_") and os.path.isfile(os.path.join(TMP_PATH,f)):
        try:
            with open(os.path.join(TMP_PATH,f),"r") as fileread:
                read_result.append(json.loads(fileread.read()))
                result_files.append(f)
        except Exception as e:
            logging.error(str(e))
            continue


for f_name,f_data in zip(result_files,read_result):
    report = {"status": "True"}
    try:
        esdata = ESDataSend(es,es_init_indices,f_data)
        tmp = list()
        for i in esdata.rawdata:
            tmp.extend(esdata.compile_chunk_data(i))
        result = esdata.normalize(tmp)
        send_result = send_data(es,result)
        logging.debug(send_result)
    except Exception as e:
        logging.error(str(e))
        report["status"] = "False"
    _id = f_name.replace("rslt_","")
    print(f_name)
    _id = _id.split("-")[0]
    conf = es.get(index="crawler_config",id=_id)
    conf["_source"].update(report)
    es.index(index="crawler_config",body=conf["_source"],id=_id)