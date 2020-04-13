import yaml
import json
import requests
import jmespath
import json
import hashlib
import copy

from time import sleep

from elasticsearch import Elasticsearch
from elasticsearch import helpers

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from crawler.libs.util import *
from crawler.libs.extractors import *
from crawler.libs.app import update_scraper_status
from crawler.settings import *
from crawler import logging


"""
Product Crawler class inherit company details from Company Details class.
It will generate crawlers which will be appended to Worker's tasks list"""


CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
if not CHROMEDRIVER_PATH:
    CHROMEDRIVER_PATH = get_path('chromedriver')

IS_REMOTE = os.getenv("REMOTE_DRIVER","0")
REMOTE_HOST = os.getenv("REMOTE_HOST","localhost")
REMOTE_PORT = os.getenv("REMOTE_PORT","4444")

class Worker(object):

    driverType = "chrome"
    driverPath = CHROMEDRIVER_PATH
    driver = None
    is_headless = True
    task_ = list()

    def __init__(self,headless=True, *args, **kwargs):
        task_ = list()
        options = Options()
        if headless:
            #options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--user-agent='Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'")        
        if IS_REMOTE == "1":
            print("========================= Using Remote WebDriver ===============================")
            self._remote_webdriver = True
            host = "http://{}:{}/wd/hub".format(REMOTE_HOST,REMOTE_PORT)
            self.driver = webdriver.Remote(host,DesiredCapabilities.CHROME)
        else:
            self._remote_webdriver = False
            self.driver = webdriver.Chrome(self.driverPath, options=options)

    def get(self,url):
        self.driver.get(url)
        self.action = ActionChains(self.driver)

class CompanyDetails(object):
    base_url = None
    company_name = None
    product_list = None

    def __init__(self, **kwargs):
        self.base_url = None
        self.company_name = None
        self.product_list = list()
        self.currency = None
        if kwargs:
            for key, value in kwargs.items():
                try:
                    setattr(self, key, value)
                except:
                    logging.error("Can not set value")
                    pass

    @property
    def company_detail(self):
        d = {
            "nm_company": self.company_name,
            "base_url": self.base_url.rstrip("/"),
            "currency_used": self.currency_used
        }
        return d

class ProductCrawler(CompanyDetails):
    product_name = None
    endpoint = None
    type_ = None
    content = list()
    worker = None
    driver = None
    failure_count = 0
    is_template_path = False
    is_template_content = False
    with_action = False
    chain_query = list()
    display = None
    skip = False
    content_result = list()
    is_headless = False
    dump_to_database = True
    status_html_content = False
    status_crawler = False
    ignore_none = None
    currency_used = None
    window_size = False

    def __init__(self, config, *args, **kwargs):
        super(ProductCrawler, self).__init__(**config)
        self.content = {}
        self.action_chains = list()
        self.chain_query = list()
        self.date_time = get_time()
        for key, value in kwargs.items():
            if key == 'name':
                self.product_name = value
            elif key == 'endpoint':
                self.endpoint = value
            elif key == 'type':
                self.type_ = value
            elif key == 'data_display':
                self.display = value
            elif key == 'content':
                for i in value:
                    content_ = self.parse_content(i)
                    self.content = {**self.content, **content_}
            elif key == 'skip_first_data':
                self.skip = True
            elif key == 'currency_used':
                self.currency_used = value
            elif key == 'dump_to_database':
                self.dump_to_database = value
            elif key == 'is_headless':
                self.is_headless = value
            elif key == 'ignore_none':
                self.ignore_none = value
            elif key == 'window_size':
                try:        
                    value = flatten_dictionaries(value)
                    self.window_size_x = int(value['x'])
                    self.window_size_y = int(value['y'])
                    self.window_size = True
                except Exception:
                    pass
            elif key == 'action_chains':
                chain_query = list()
                self.with_action = True
                for i in value:
                    for key, val in i.items():
                        chain_name = key
                        chain = self.parse_action_chains(val)
                        d = {'chain_name': chain_name, 'chain': chain}
                    self.chain_query.append(d)
            else:
                raise ValueError("Wrong Configuration")
    @property
    def product_detail(self):
        time = get_time()
        d = {
            "nm_product_type": self.type_,
            "nm_product": self.product_name,
            "nm_endpoint": self.endpoint,
            "datetime": str(time),
            "content" : None
        }
        return d

    def write_result(self,crawl_result):
        self.content_result = (crawl_result)

    def crawler_result(self):
        result = self.product_detail
        result['content'] = self.content_result
        return result

    def flatten_data_result(self):
        product_detail = {"nm_product_type": self.type_, "nm_product": self.product_name, "date": str(get_time())}
        product_detail = {**product_detail, **self.company_detail}
        result = self.product_detail
        result['content'] = self.content_result
        datasets = list()
        _sort = copy.deepcopy(self.content_result)
        for key, val in _sort.items():
            if key == 'additional_features' or key == 'additional':
                for i in val:
                    i['date'] = product_detail['date']
            else:
                for i in val:
                    i = i.update(product_detail)
        return _sort


    def get_url(self):
        return self.base_url + self.endpoint

    def is_dynamic(self):
        """ Is templating used? """
        return self.is_template_path or self.is_template_content

    def config_worker(self):
        self.worker = Worker(self.is_headless)
        worker = self.worker
        url = self.get_url()
        worker.get(url)
        wait = get_loaded(worker.driver)
        if not wait:
            logging.error("Page not loaded")
        self.driver = worker.driver
        if self.window_size:
            logging.debug("Resizing {} x {}".format(self.window_size_x,self.window_size_y))
            self.driver.set_window_size(int(self.window_size_x),int(self.window_size_y))
        else:
            self.driver.maximize_window()
        self.action = worker.action
        self.config_action_chains()

    def config_action_chains(self):
        if self.with_action:
            action_chains = list()
            chain = self.chain_query
            for i in range(0,len(chain)):
                _iter = chain[i]
                tmp = ActionsHandler(self.action, self.driver, 
                                     _iter['chain'], _iter['chain_name'])
                action_chains.append(tmp)
            self.action_chains = action_chains

    def obtain_value(self):
        contents = self.content
        for k, v in contents.items():
            for i in v:
                i.extractor.driver = self.driver

    def parse_action_chains(self, actions):
        chains = list()
        for action in actions:
            for act, query in action.items():
                d = {}
                q_ = flatten_dictionaries(query)
                d[act] = q_
                chains.append(d)    
        return chains

    def parse_content(self, content=list()):
        content_handler = list()
        contents = ContentHandler(content)
        return contents.get_value()

    def check_html_changes(self):
        new_content = self.get_html_content()
        old_content = self.html_content
        if not old_content:
            self.get_html_content(dump=True)
            return True
        elif new_content != old_content:
            msg = "Content changed detected on endpoint : {}\nOld:{}\nNew:{}".format(self.endpoint,old_content,new_content)
            logging.warning(msg)
            self.get_html_content(dump=True)
            self.status_html_content = False
            return False
        else :
            self.status_html_content = True
            return True


    def get_html_content(self,dump=False):
        url = self.get_url()
        try:
            content = get_page(url)
            content = content.text.encode('utf-8')
            content = hashlib.sha224(content).hexdigest()
        except Exception as e:
            tmp_worker = Worker(headless=True)
            driver = tmp_worker.driver
            driver.get(url)
            elem = driver.find_element_by_xpath("//body")
            content = elem.get_attribute("innerHTML")
            content = content.encode('utf-8')
            content = hashlib.sha224(content).hexdigest()
            driver.quit()
        if dump:
            filename = self.endpoint.replace("/","__")
            filename = "{}_{}".format(self.company_name,filename) + ".txt"
            file_path = "{}/{}".format(HTML_LOCATION,filename)
            file_path = get_path(file_path)
            generate_file(file_path,content)
        else:
            return content

    @property
    def html_content(self):
        try:
            filename = self.endpoint.replace('/','__')
            filename = "{}_{}".format(self.company_name,filename) + ".txt"
            path = '{}/{}'.format(HTML_LOCATION,filename)
            pathfile = get_path(path)
            data = read_file(pathfile)
            if data:
                return data
            else:
                return None
        except Exception as e:
            return None

    def filter_ignored(self,data,ignore_value=None):
        ignore_value = self.ignore_none
        if not ignore_value:
            return data
        else:
            result = list()
            for i in data:
                is_pass = True
                for key in ignore_value:
                    try:
                        if i[key].lower() == 'none' or i[key] == '':
                            is_pass = False
                            break
                    except Exception:
                        continue
                if is_pass:
                    result.append(i)
            return result

#   Obtain data for every action in action chains. 
    def run(self):
        count = 0
        logging.debug(self.get_url())
        if self.action_chains:
            self.obtain_value()
            data = list()
            if not self.skip:
                data.append(self.write_value())
            for action in self.action_chains:
                for i in range(0, action.repeat):
                    action.run()
                    self.obtain_value()
                    data.append(self.write_value())
        else:
            self.obtain_value()
            data = [(self.write_value())]
        return data

    def warm_up(self):
        action = self.action_chains[0]
        action.run()

    def write_value(self):
        data = dict()
        for key, value in self.content.items():
            val = list()
            for item in value:
                if item.is_preaction:
                    item._configure_preactions(self.action,self.driver)
                content_ = item.dump_value()
                val.append(content_)
            data[key] = flatten_list(val)
        return data 

    def sort_data(self,data):
        for row in data:
            pass
    
    def normalize(self,data):
        displayType = self.display
        result_tmp = None
        if displayType == 'slider':
            tmp = DataSorter(data,displayType)
            result_tmp = tmp.sorted_data
        else:
            keys = list()
            resultTmp = list()
            for i in data:
                tmp = DataSorter(i,displayType)
                tmp_data = tmp.sorted_data
                resultTmp.append(tmp_data)
                tmp_key = [i for i in tmp_data.keys() if i not in keys ]
                keys += tmp_key
            d = {}
            for i in keys:
                d[i] = list()
                for row in resultTmp:
                    d[i] += row[i]
            result_tmp = d
        result = {}
        for key,value in result_tmp.items():
            result[key] = self.filter_ignored(value)
        return result

    def report_error(self):
        data = self.product_detail
        res = update_scraper_status("FAIL",data['nm_product_name'])
        return res

    def register_company(self):
        send_data = {
            "nm_company" : self.company_name,
            "url_company": self.base_url,
            "currency_used": self.currency_used
        }

class ContentHandler(ProductCrawler):
    content_name = None

    def __init__(self,items):
        for key,val in items.items():
            self.parse_items(val)
            self.content_name = key

    def get_value(self):
        return {self.content_name: self.extractors_}


    def parse_items(self,item):
        extractors_ = list()
        item = flatten_dictionaries(item)
        for key, value in item.items():
            contentValue = flatten_dictionaries(value)
            for key_, val in contentValue.items():
                if key_.lower() == 'extractor':
                    tmp = flatten_dictionaries(val)
                    config = self.build_extractor_configuration(tmp)
                    extractor = Extractors(**config)
                    extractor.value_name = key
                elif key_.lower() == 'postprocess':
                    extractor.is_postprocessed = True
                    extractor.postprocess = val
                elif key_.lower() == 'pre_actions':
                    extractor.is_preaction = True
                    chain_queries = list()
                    for i in val:
                        for pkey,pval in i.items():
                            chain_name = key+' preactions'
                            chain = self.parse_action_chains(pval)
                            chain_query = {'chain_name': chain_name, 'chain': chain}
                        chain_queries.append(chain_query)
                    extractor._pre_actions = chain_queries
            extractors_.append(extractor)
        self.extractors_ = extractors_

    def build_extractor_configuration(self, value):
        d = {"type_": None, 
             "value": None,
             "static": False,
             "attribute": None,
             "properties": None,
             "driver": self.driver}
        for key, val in value.items():
            if key.lower() == 'attribute' or key.lower() == 'attributes':
                d['attribute'] = val
            elif key.lower() == 'property' or key.lower() == 'properties':
                d['attribute'] = val
            elif key.lower() == 'static':
                d['static'] = True
            else:
                d['type_'] = key
                d['value'] = val
        return d


def dict_list_to_list_dict(data):
    if isinstance(data, dict):
        d = list()
        for key, val in data.items():
            for i in val:
                d.append({key: val})
    return d


class DataSorter(object):
    raw_data = None
    display_type = None

    def __init__(self, data, display):
        self.raw_data = data
        self.display_type = display.lower()

    @property
    def sorted_data(self):
        return self.sort_data()

    def sort_data(self):
        display = self.display_type
        data = self.raw_data
        if display == 'slider':
            result = self.slider_sorter(data)
        elif display == 'card':
            result = self.card_sorter(data)
        else:
            raise ValueError("Unidentified display type")
        return result

    def slider_sorter(self, data):
        keys = list(data[0].keys())
        result = dict.fromkeys(keys, [])
        for i in data:
            for key, value in i.items():
                result[key] = result[key]+[flatten_data(flatten_dictionaries(value))]
        return result

    def group_data(self,data):
        for row in data:
            pass


    def card_sorter(self, data):
        retdat = {}
        for key, value in data.items():
            data_ = flatten_dictionaries(value)
            processedData = list()
            keys = list(data_.keys())
            static_value = {}
            max_index = max([len(val) for val in data_.values()])
            for x in range(0, max_index):
                d = {}
                for i in keys:
                    try:
                        if isinstance(data_[i][x],dict):
                            static_value[i] = data_[i][x]['static']
                            d[i] = data_[i][x]['static']
                        else:
                            d[i] = str(data_[i][x])
                    except IndexError:
                        str_check = "{} in {} : {}".format(i,static_value,i in static_value)
                        if i in static_value:
                            d[i] = static_value[i]
                        else:
                            d[i] = "None"
                check = list(d.values())
                if all('' == str(s) or str(s).isspace() for s in check):
                    continue
                processedData.append(d)
            retdat[key] = processedData
        return retdat


def get_loaded(driver,count=0):
    try:
        myElem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//body')))
        return True
    except TimeoutException:
        driver.refresh()
        logging.error("Loading is too long")
        if count < 3:
            get_loaded(count=count+1)
        else:
            return False

def generate_id(stringdata):
    myid = hashlib.md5(stringdata.encode('utf8')).hexdigest()
    return myid

def send_bulk(es,dataset):
    actions = list()
    for i in dataset:
        _id = i.pop("_id")
        _index = i.pop("_index")
        template = {
        "_index": _index,
        "_id": _id
        }

        _tmp = { "_source": {"timestamp": str(datetime.datetime.now().today())}}
        _tmp['_source'].update(i)
        template.update(_tmp)
        actions.append(template)
    res = helpers.bulk(es, actions)
    return res

class ESDataSend(object):

    def __init__(self, es, cfg, rawdata):
        if not isinstance(rawdata,list):
            raise TypeError("rawdata must be list")
        self.rawdata = rawdata
        self.elastic_search = es
        self.config = cfg
    
    def compile_chunk_data(self, rawdata):
        merged = list()
        length = len(rawdata['pricing'])
        additional = rawdata.get("additional_features",False)
        if additional:
            for i in range(0,length-1):
                add = {"additional_features" : rawdata['additional_features'][i]}
                d = {**rawdata['pricing'][i], **add}
                merged.append(d)
        else:
            merged = rawdata['pricing']
        self.chunk_data = merged
        return merged
    
    def normalize(self,dataset):
        result = list()
        for data in dataset:
            product_type = data['nm_product_type']
            try:
                self.config[product_type]
            except KeyError:
                msg = "index {} must be initiated on configuration"
                logging.error(msg)
                return list()
            else:
                __datatmp = dict()
                __datatmp["_index"] = product_type
                for key,val in self.config[product_type].items():    
                    required = self.config[product_type][key].get('required',False)
                    if required:
                        try:
                            __datatmp[key] = data[key]
                        except KeyError:
                            logging.error(data)
                            msg = "{} is required for product type {}".format(key,product_type)
                            logging.error(msg)
                            return list()
                    else:
                        __datatmp[key] = data.get(key,"None")
            _tmp = __datatmp.copy()
            _tmp.pop('date',None)
            _id = json.dumps(_tmp)
            _id = generate_id(_id)
            __datatmp['_id'] = _id
            result.append(__datatmp)
            if 'additional_features' in data.keys():
                parent_id = _id
                __datatmp_add = {"_parent_id": parent_id, "_parent_index": product_type, "_index": "additional_features"}
                __datatmp_add = {**__datatmp_add, **data['additional_features']}
                _tmp = dict()
                _tmp = __datatmp_add.copy()
                _tmp.pop('date',None)
                _id = json.dumps(_tmp)
                _id = generate_id(_id)
                __datatmp_add["_id"] = _id
                result.append(__datatmp_add)
        return result
