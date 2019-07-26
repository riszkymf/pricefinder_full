import requests
from crawler.settings import *
import json
import copy
from crawler.libs.util import get_time

def post_requests(endpoint,data,headers=None):
    endpoint = endpoint.lstrip("/")
    headers = {"Content-Type": "application/json"}
    url = "{}/{}".format(APP_URL,endpoint)
    res = requests.post(url,data,headers=headers)
    return res

def build_json(command,data):
    send_data = {}
    if command == "insert":
        send_data = {
            "insert":{
                "fields": data
            }
        }
    if command == "remove":
        send_data = {
            "remove":{
                "tags": data
            }
        }
    if command == "where":
        send_data = {
            "where":{
                "tags": data
            }
        }
    if command == "view":
        send_data = {
            "view":{
                "tags": data
            }
        }
    if command == 'update':
        send_data = {
            "update": {
                "tags": data["tags"],
                "fields":data["fields"]
            }
        }
    
    return json.dumps(send_data)

def register_company(data):
    companyDetails = {
        "nm_company": data["nm_company"].lower(),
        "url_company": data["base_url"],
        "currency_used": data["currency_used"]
    }
    
    data_send = {"nm_company": companyDetails['nm_company']}
    data_send = build_json("where",data_send)
    response = post_requests("/api/company",data_send)
    tmp = response.json()
    if tmp['data']:
        return response
    else:
        data_send = {"url_company": companyDetails['url_company']}
        data_send = build_json("where",data_send)
        response = post_requests("/api/company",data_send)
        tmp = response.json()
        if tmp['data']:
            return response
        else:
            insert_json = build_json("insert",companyDetails)
            result = post_requests("/api/company",insert_json)
            return result

def register_product_type(data):
    productDetails = {
        "nm_product": i["nm_product"],
        "nm_databaseref": i["nm_database_ref"]
    }
    
    data_send = {"nm_product": productDetails['nm_product']}
    data_send = build_json("where",data_send)
    response = post_requests("api/product",data_send)
    tmp = response.json()
    if tmp['data']:
        return response
    else:
        data_send = {"nm_databaseref": productDetails['nm_databaseref']}
        data_send = build_json("where",data_send)
        response = post_requests("api/product",data_send)
        tmp = response.json()
        if tmp['data']:
            return response
        else:
            insert_json = build_json("insert",productDetails)
            result = post_requests("api/product",insert_json)
            return result

def register_worker(data):
    productDetails = {
        "loc_schedule_config": i["loc_schedule_config"],
        "loc_config": i["loc_config"]
    }
    
    data_send = {"loc_config": productDetails['loc_config']}
    data_send = build_json("where",data_send)
    response = post_requests("/api/worker",data_send)
    tmp = response.json()
    if tmp['data']:
        return response
    else:
        insert_json = build_json("insert",productDetails)
        result = post_requests("/api/product",insert_json)
        return result

def find_id(data,endpoint):
    data = build_json('where',data)
    try:
        res = post_requests(endpoint,data)
        res = res.json()
        result = res['data']
    except Exception as e:
        print(str(e))
        result = None
    return result

def register_company_product(company,data=None):
    company = company.lower()
    id_company = find_id({"nm_company": company},'/api/company')
    try:
        id_company = id_company[0].get('id_company',None)
    except Exception:
        id_company = None
    nm_product = data['nm_product_name']
    product_type = data["nm_product_type"]
    id_product = find_id({"nm_product": product_type},'/api/product')
    try:
        id_product = id_product[0].get('id_product',None)
    except Exception:
        id_product = None

    d = {
        "nm_company_product": nm_product,
        "id_company": str(id_company),
        "id_product": str(id_product),
        "id_worker": str(402140815780249601)
    }

    json_data = build_json("insert",d)
    res = post_requests('/api/company_product',json_data)
    result = res.json()
    return result


def register_content(result_data,id_company_product,nm_company_product=None):
    failures = list()
    result = list()
    type_ = result_data['nm_product_type']
    if type_.lower() == 'vm' and 'pricing' in result_data['content']:
        result = register_vm(result_data,id_company_product,nm_company_product)
    elif type_.lower() == 'hosting' and 'pricing' in result_data['content']:
        result = register_hosting(result_data,id_company_product,nm_company_product)
    if "additional_features" in result_data['content']:
        additional_data = result_data['content']['additional_features']
    else:
        additional_data = [{}]
    additional_result = register_additional_features(additional_data,id_company_product,nm_company_product)
    failures =  result + additional_result
    return failures


def register_hosting(input_data,id_company_product,nm_company_product=None):
    json_template = {
        "id_company_product": None,
        'spec_price': None,
        "spec_storage": None,
        'spec_database': None,
        "spec_free_domain": None,
        "spec_hosting_domain": None,
        'spec_subdomain': None,
        "spec_ftp_user": None,
        "spec_control_panel": None,
        'spec_email_account': None,
        "spec_spam_filter": None,
        "date_time": None
    }
    fields = list(json_template.keys())
    if not id_company_product:
        nm_company_product = input_data['nm_product_name']
        json_data = build_json('where',{"nm_company_product": nm_company_product})
        res = post_requests('api/company_product',json_data)
        res = res.json()
        id_company_product = res['data'][0]['id_company_product']
    
    failure = list()
    for row in input_data['content']['pricing']:
        d_send = {}
        for field in fields:
            d_send[field] = str(row.get(field,'NONE'))
        d_send['date_time'] = input_data['datetime']
        d_send['id_company_product'] = str(id_company_product)
        json_send = build_json('insert',d_send)
        res = post_requests('api/hosting',json_send)
        if find_failure(res):
            failure.append(row)
            print(d_send)    
    return failure


def register_vm(input_data,id_company_product,nm_company_product=None):
    json_template = {
            "id_company_product": None,
            "spec_vcpu": None,
            'spec_clock': None,
            "spec_ram": None,
            "spec_os": None,
            "spec_storage_volume": None,
            'spec_ssd_volume': None,
            "spec_snapshot_volume": None,
            "spec_template_volume": None,
            'spec_iso_volume': None,
            "spec_public_ip": None,
            "spec_backup_storage": None,
            'spec_price': None,
            "spec_notes": None,
            "date_time": None
        }
    fields = list(json_template.keys())
    if not id_company_product:
        nm_company_product = input_data['nm_product_name']
        json_data = build_json('where',{"nm_company_product": nm_company_product})
        res = post_requests('api/company_product',json_data)
        res = res.json()
        id_company_product = res['data'][0]['id_company_product']
    failure = list()
    for row in input_data['content']['pricing']:
        d_send = {}
        for field in fields:
            d_send[field] = str(row.get(field,'NONE'))
        d_send['date_time'] = input_data['datetime']
        d_send['id_company_product'] = str(id_company_product)
        json_send = build_json('insert',d_send)
        res = post_requests('api/vm',json_send)
        if find_failure(res):
            failure.append(row)
            print(d_send)    
    return failure

    

def register_additional_features(input_data,id_company_product,nm_company_product=None):
    json_template = {
        "id_company_product": None,
        'spec_features': None,
        "spec_features_price": None,
        "spec_features_value": None
        }
    fields = list(json_template.keys())
    if not id_company_product:
        json_data = build_json('where',{"nm_company_product": nm_company_product})
        res = post_requests('api/company_product',json_data)
        res = res.json()
        id_company_product = res['data'][0]['id_company_product']

    failure = list()
    for row in input_data:
        d_send = {}
        if row:
            for key,value in row.items():
                if key.lower() == 'spec_features_price':
                    continue
                else:
                    d_send['spec_features'] = str(key)
                    d_send['spec_features_value'] = str(value)
                d_send['spec_features_price'] = str(row.get('spec_features_price','NONE'))
                d_send['id_company_product'] = str(id_company_product)
                json_send = build_json('insert',d_send)
                res = post_requests('api/additional_features',json_send)
                if find_failure(res):
                    failure.append(row)
                    print(d_send)    
        else:
            for field in fields:
                d_send[field] = str(row.get(field,'NONE'))
            d_send['id_company_product'] = str(id_company_product)
            json_send = build_json('insert',d_send)
            res = post_requests('api/additional_features',json_send)
            if find_failure(res):
                failure.append(row)
                print(d_send)    
    return failure

def find_failure(res):
    if res.status_code != 200:
        return True
    elif res.status_code == 200:
        data = res.json()
        status = data['message']['status']
        if not status:
            print(data['message'])
        return not(status)

def update_scraper_status(status,nm_company_product=None):
    data_find = {"nm_company_product": nm_company_product}
    try:
        id_company_product = find_id(data_find,'api/company_product')[0]['id_company_product']
        tmp = {"tags": {"id_company_product": id_company_product},"fields": {"status_page": str(status)}}
        data_send = build_json('update',tmp)
        res = post_requests('api/company_product',data_send)
        return res
    except Exception:
        return None

def send_conf_data(conf_data,conf_name):
    endpoint = 'api/config'
    date_time = get_time()
    send_data = {
        "conf_nm": conf_name,
        "conf_data": conf_data,
        "date_time": date_time
    }
    send_data = build_json("insert",send_data)
    res = post_requests(endpoint,send_data)
    return res

def update_worker_status(status,headers=None):
    data = {
        "tags" :
            {"id_worker": ID_WORKER},
        "fields":
        {
            "loc_config": LOC_CONFIG,
            "loc_schedule_config": LOC_SCHEDULE_CONFIG,
            "status_worker": status
            }
    }
    json_send = build_json("update",data)
    res=post_requests('api/worker',json_send,headers)
    return res