from elasticsearch import helpers 
from app import logging

import json
import datetime
import hashlib

timeformat_short = "%Y-%m-%d"
timeformat_long = "%Y-%m-%d %H:%M:%S"



def send_bulk(es,indexed_data):
    for index,datas in indexed_data.items():
        actions = list()
        for i in datas:
            _id = i.pop("id")
            template = {
            "_index": index,
            "_type": index,
            "_id": _id,
            }

            _tmp = { "_source": {"timestamp": datetime.datetime.now()}}
            _tmp['_source'].update(i)
            template.update(_tmp)
            logging.debug(template)
            actions.append(template)
        res = helpers.bulk(es, actions)
    return res

def search_data(es,index,search_query=None):
    res = es.search(index=index, body=search_query)
    return res

def scan_data(es,index,search_query=None):
    res = helpers.scan(es,index=index,query=search_query)
    return list(res)