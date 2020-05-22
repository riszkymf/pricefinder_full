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

def __configure_elasticsearch(es,conf):
    keys = list(conf.keys())
    for key in keys:
        try:
            res = es.indices.create(index=key, ignore=[400,404])
            logging.debug(res)
        except Exception as e:
            logging.error(str(e))
        _settings = conf[key].get('_settings',dict())
        _alias = _settings.get('aliases',list())
        if _settings and _alias:
            for i in _alias:
                try:
                    res = es.indices.put_alias(index=key,name=i)
                    logging.debug(res)
                except Exception as e:
                    logging.error(str(e))
    


