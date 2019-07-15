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
    files = get_all(path)
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
                print(res)

def run(path=CONF_PATH,force_headless=False,force_dump=True,dump_location=DUMP_LOCATION):
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
                dd=d.run()
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