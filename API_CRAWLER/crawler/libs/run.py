from ..libs.util import *
from ..libs.handler import *
from ..libs.app import *
from crawler.settings import *
from datetime import datetime
import json
import requests
from celery import Celery

celery_app = Celery(CELERY_APP_NAME,broker=CELERY_BROKER,timezone=CELERY_TIMEZONE)

def load_crawler_configuration(path):
    files = load_config(path)
    f_yaml = list()
    for f in files:
        try:
            tmp = load_yaml(f)
        except Exception as e:
            print("Error {} ".format(str(e)))
            continue
        finally:
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
                nm_company_product = d.product_detail['nm_product_name']
                res=update_scraper_status(check,nm_company_product=nm_company_product)

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
                    print(str(e))
                    print(d.company_detail)
                    print(d.product_detail)
                    d.report_error()
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
    if crawler_result and force_dump:
        failure['send'] = register_data(crawler_result)
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
                nm_company_product = item['nm_product_name']
            result = register_content(item,id_company_product,nm_company_product)
            fail = fail+result
    return fail

class CrawlerExecutor(object):
    _path = None
    dump_location = DUMP_LOCATION
    is_scrape = False
    is_check_content = False
    stack_send = False
    
    def __init__(self,path=CONF_PATH, scrape=False, check_content=False, **kwargs):
        self._paths = load_config(path)
        self._path = path
        self.is_scrape = scrape
        self.check_content = check_content
        for key,value in kwargs.items():
            setattr(self,key,value)
            
        self.configure_crawler()
        
    def load_crawler_configuration(self,path):
        files = load_config(path)
        f_yaml = list()
        for f in files:
            try:
                tmp = load_yaml(f)
            except Exception as e:
                print("Error {} ".format(str(e)))
                continue
            finally:
                f_yaml.append(tmp)
        return f_yaml

    def configure_crawler(self):
        _handler = list()
        status = {"sent": None,"scrape":None}
        conf = self.load_crawler_configuration(self._path)
        for i,j in zip(conf,self._paths):
            d = {"path": None, "crawler_configuration": list()}
            cfg = flatten_dictionaries(i[0]['config'])
            cfg['company_name'] = cfg.pop('name')
            configuration = list()
            for row in i:
                if 'product' not in row:
                    continue
                else:
                    products = row['product']
                    _products = flatten_dictionaries(products)
                    dd = ProductCrawler(cfg,is_headless=False,**_products)
                    configuration.append({"config": dd, "status": status})
            d['path'] = j
            d['crawler_configuration'] = configuration
            d['company_configuration'] = cfg
            _handler.append(d)
        self._handler = _handler
        return _handler
    
    @property
    def crawler_configs(self):
        return self._handler
    
    
    
    @property
    def runner_status(self):
        keys = ["sent","failure"]
    
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
                nm_company_product = crawler.product_detail['nm_product_name']
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
        write_to_json = {"company": None, "data": list()}
        print("\n==========================================\n")
        for config in configs:
            crawler = config['config']
            _company_details = crawler.company_detail
            print(crawler.endpoint)
            crawler.config_worker()
            crawler.register_company()
            try:
                scraped_data = crawler.run()
            except Exception as e:
                print(str(e))
                config['status']['scrape'] = {"status" : False, "message": str(e)}
            else:
                config['status']['scrape'] = {"status": True, "message": "Success"}
                normalized_data = crawler.normalize(scraped_data)
                crawler.write_result(normalized_data)
                for key,value in normalized_data.items():
                    if not value:
                        config['status']['scrape'] = {"status": False, "message": "No Result!"}
                        break
                    _tmp = crawler.crawler_result()
            crawler.driver.quit()
            result['company'] = _company_details
            result['data'].append(crawler.crawler_result())
            if not runner_configs['stack_send']:
                config = self.register_data(result,config)
            print(config['status'])
        return configs

    def register_data(self,data,config):
        company_details = data['company']
        company_name = company_details["nm_company"]
        result = register_company(company_details)
        for item in data['data']:
            res = register_company_product(company_name,item)
            nm_company_product = None
            try:
                id_company_product = res['message']['id']
            except Exception:
                id_company_product = None
                nm_company_product = item['nm_product_name']
            result = register_content(item,id_company_product,nm_company_product)
            if not result:
                config['status']['sent'] = {"status":True, "message": "Success"}
            else:
                config['status']['sent'] = {"status": False, "message": result}
        return config
            
    def register_stacked_data(self,data):
        fail = list()
        for row in data:
            result = register_company(company_details)
            company_name = company_details["nm_company"]
            for item in row['data']:
                res = register_company_product(company_name,item)
                nm_company_product = None
                try:
                    id_company_product = res['message']['id']
                except Exception:
                    id_company_product = None
                    nm_company_product = item['nm_product_name']
                result = register_content(item,id_company_product,nm_company_product)
                fail = fail+result
        return fail