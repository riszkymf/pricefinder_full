from ..libs.util import *
from ..libs.handler import *
from ..libs.app import *
from crawler.settings import *
from crawler import logging
from datetime import datetime
import json
import requests
from celery import Celery



def load_crawler_configuration(path):
    files = load_config(path)
    f_yaml = list()
    for f in files:
        try:
            tmp = load_yaml(f)
        except Exception as e:
            logging.error("Error {} ".format(str(e)))
            continue
        else:
            f_yaml.append(tmp)
    return f_yaml
    
def content_check(path=CONF_PATH):
    configs = load_crawler_configuration(path)
    for datas in configs:
        result = {"company": None, "data": list()}
        cfg = datas[0]
        cfg =flatten_dictionaries(cfg['config'])
        cfg['company_name'] = cfg.pop('name')
        for row in datas:
            if 'product' not in row:
                continue
            else:
                prods = flatten_dictionaries(row['product'])
                d = ProductCrawler(cfg,**prods)
                check = d.check_html_changes()
                nm_company_product = d.product_detail['nm_product']
                #res=update_scraper_status(check,nm_company_product=nm_company_product)

def run(path=CONF_PATH,force_headless=False,force_dump=True,dump_to_json=False,dump_location=DUMP_LOCATION):
    crawler_result = list()
    configs = load_crawler_configuration(path)
    failure = {
        "send": list(),
        "scrape": list()
    }
    for datas in configs:
        result = list()
        result_ = {"company": None, "data": list()}
        write_to_json = {"company": None, "data": list()}
        cfg = datas[0]
        cfg = flatten_dictionaries(cfg['config'])
        cfg['company_name'] = cfg.pop('name')
        product_details = {}
        for row in datas:
            if 'product' not in row:
                continue
            else:
                prods = row['product']
                prods_ = flatten_dictionaries(prods)
                d = ProductCrawler(cfg,is_headless=force_headless,**prods_)
                _company_details = d.company_detail
                d.config_worker()
                d.register_company()
                try:
                    dd=d.run()
                except Exception as e:
                    logging.error(str(e))
                else:
                    normalized_data = d.normalize(dd)
                    d.write_result(normalized_data)
                    for key,value in normalized_data.items():
                        if not value:
                            failure['scrape'].append(d.endpoint)
                            break
                    _tmp = d.crawler_result()
                    if d.dump_to_database :
                        result_['data'].append(_tmp)
                    write_to_json['data'].append(_tmp)
                    d.driver.quit()
                    result.append(dd)
        result_['company'] = _company_details
        write_to_json['company'] = _company_details
        if dump_json_data:
            dump_json_data(write_to_json)
        crawler_result.append(result_)
    return crawler_result

def dump_json_data(data):
    company = data['company']['nm_company']
    filename = "{}.json".format(company.lower())
    path = DUMP_LOCATION + "/" + filename
    generate_file(path,json.dumps(data))



def register_data(data):
    fail = list()
    for row in data:
        company_details = row["company"]
        result = register_company(company_details)
        company_name = company_details["nm_company"]
        for item in row['data']:
            res = register_company_product(company_name,item)
            nm_company_product = None
            try:
                id_company_product = res['message']['id']
            except Exception:
                id_company_product = None
                nm_company_product = item['nm_product']
            result = register_content(item,id_company_product,nm_company_product)
            fail = fail+result
    return fail

    
class CrawlerExecutor(object):
    _path = None
    _handler = None
    _sent = list()
    _failure = list()
    dump_location = DUMP_LOCATION
    is_scrape = False
    is_check_content = False
    stack_send = False
    scrape_result = None
    force_dump = False
    flattened_data = list()
    
    def __init__(self,json_config=list(), scrape=False, check_content=False, **kwargs):
        self.is_scrape = scrape
        self.check_content = check_content
        for key,value in kwargs.items():
            setattr(self,key,value)
        if not json_config:
            raise ValueError("Configuration is Empty")
        else:
            self._config =  json_config
        self.configure_crawler()
        self.flattened_data = list()
        
    def load_crawler_configuration(self,path):
        files = load_config(path)
        try:
            result = load_yaml(f)
        except Exception as e:
            logging.error("Error {} ".format(str(e)))
        return result

    def configure_crawler(self):
        status = {"sent": None,"scrape":None}
        conf = self._config
        cfg = flatten_dictionaries(conf[0]['config'])
        cfg['company_name'] = cfg.pop('name')
        configuration = list()
        for row in conf:
            if 'product' not in row:
                continue
            else:
                products = row['product']
                _products = flatten_dictionaries(products)
                dd = ProductCrawler(cfg,is_headless=False,**_products)
                configuration.append({"config": dd, "status": status})
        self._handler = configuration
        return configuration
    
    @property
    def crawler_configs(self):
        return self._handler
       
    
    def validate_config(self,es_config):
        configs = self._handler
        for i in configs:
            type_ = i['config'].type_
            extractors = i["config"].content.get("pricing",list())
            if not extractors:
                continue
            keys = [i.value_name for i in extractors]
            product = es_config[type_]
            required_keys = [key for key,val in product.items() if val['required'] and 'spec' in key]
            check = set(required_keys).issubset(set(keys))
            if not check:
                missing_fields = set(required_keys) - set(keys)
                print("product {} is missing {}".format(type_,list(missing_fields)))
                return False

        return True


    @crawler_configs.setter
    def crawler_configs(self,value):
        index = value[1]
        value_ = value[0]
        for i in value_:
            status = i['status']
            if not (status['scrape']['status'] and status['sent']['status']):
                _stat = i.copy()
                self._failure.append(i)
            else:
                self._sent.append(i)
        logging.debug(self._failure)
        self._handler[index] = value_

    @property
    def runner_status(self):
        _stat = {
            "sent": self._sent,
            "failure": self._failure
        }
        return _stat
    
    def check_duplicate(self,data,remove=True):
        __pricing = data.get('pricing',[{}])
        __additional = data.get('additional_features',[])
        __check = True
        __len = len(__pricing)
        if not __additional:
            for item in __pricing:
                if __pricing.count(item) > 1:
                    logging.warning("Found duplicate, value :{}".format(item))
            if remove:
                __pricing_tmp = [json.dumps(i) for i in __pricing]
                __pricing_tmp = list(set(__pricing_tmp))
                __pricing = [json.loads(i) for i in __pricing_tmp]
        data.update({"pricing":__pricing})
        if __additional:
            data.update({"additional" : __additional})
        return data
    
    @property
    def runner_configs(self):
        keys = ["force_headless","force_dump","dump_to_json","dump_location","stack_send"]
        d = {}
        for i in keys:
            d[i] = getattr(self,i,None)
        return d
    
    def content_check(self,configs=list()):
        if configs:
            for config in configs:
                crawler = config['config']
                check = crawler.check_html_changes()
                nm_company_product = crawler.product_detail['nm_product']
                res = update_scraper_status(check,nm_company_product=nm_company_product)
                
    def dump_json_data(self,data):
        company = data['company']['nm_company']
        filename = "{}.json".format(company.lower())
        path = DUMP_LOCATION + "/" + filename
        generate_file(path,json.dumps(data))
        
    def scrape(self,configs):
        runner_configs = self.runner_configs
        status = None
        result = {"company": None,"data": list()}
        result_ = {"company": None, "data": list()}
        write_to_json = {"company": None, "data": list()}
        for config in configs:            
            config['status'] = dict()
            crawler = config['config']
            _company_details = crawler.company_detail
            crawler.config_worker()
            # crawler.register_company()
            try:
                scraped_data = crawler.run()
            except Exception as e:
                logging.error(str(e))
                config['status']['scrape'] = {"status" : False, "message": str(e)}
                crawler.driver.quit()
                return configs
            else:
                config['status']['scrape'] = {"status": True, "message": "Success"}
                normalized_data = crawler.normalize(scraped_data)
                if not normalized_data:
                    return configs
                first_check = self.check_duplicate(normalized_data)
                cleaned_data = first_check
                crawler.write_result(cleaned_data)
                for key,value in normalized_data.items():
                    if not value:
                        config['status']['scrape'] = {"status": False, "message": "No Result!"}
                        break
                    _tmp = crawler.crawler_result()
            crawler.driver.quit()
            result['company'] = _company_details
            result['data'].append(crawler.crawler_result())
            self.scrape_result = result
            self.flattened_data.append(crawler.flatten_data_result())   
        return configs

