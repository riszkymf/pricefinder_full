import json

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from crawler.libs.handler import ESDataSend,generate_id
from crawler.libs.util import dump_to_tmp
from crawler import logging

class VPN_ES(object):

    def __init__(self,ES_HOST,ES_USERNAME=None,ES_PASSWORD=None):
        if ES_USERNAME == None or ES_PASSWORD == None:
            es = Elasticsearch(ES_HOST)
        else:
            es = Elasticsearch(ES_HOST,http_auth=(ES_USERNAME,ES_PASSWORD))
        self.es = es

    def test_connection(self):
        es = self.es
        try:
            es.search(index="")
        except Exception as e:
            print(str(e))
            logging.error("Failure to communicate with ElasticSearch")
            logging.error(str(e))
            raise ConnectionError("Failure to communicate with ElasticSearch")

    def obtain_configurations(self):
        es = self.es
        res = es.search(index="crawler_config", body={"query": {"match_all": {}}})

        conf_full = [i for i in res["hits"]["hits"]]
        return conf_full

    def dump_config_tmp(self,configs):
        for config in configs:
            filename = "cfg_{}-{}.json".format(config['_id'],config['_source']['config_name'])
            dump = dump_to_tmp(filename,json.loads(config['_source']['config_json']))

    def pull_configs(self):
        configs = self.obtain_configurations()
        result = self.dump_config_tmp(configs)
        return result

