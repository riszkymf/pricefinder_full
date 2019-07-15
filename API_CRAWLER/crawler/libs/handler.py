import yaml
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from crawler.libs.util import *
from crawler.module.extractors import *
from crawler.settings import *
import json
from time import sleep

"""
Product Crawler class inherit company details from Company Details class.
It will generate crawlers which will be appended to Worker's tasks list"""


DRIVER_PATH = {"chrome": get_path('chromedriver'),
               "firefox": get_path('geckodriver')}


class Worker(object):

    driverType = "chrome"
    driverPath = DRIVER_PATH['chrome']
    driver = None
    is_headless = True
    task_ = list()

    def __init__(self,headless=True, *args, **kwargs):
        task_ = list()
        options = Options()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")        
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
                    print("Can not set value")
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

    def __init__(self, config, *args, **kwargs):
        super(ProductCrawler, self).__init__(**config)
        self.content = {}
        self.action_chains = list()
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
            "nm_product_name": self.product_name,
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
        self.driver = worker.driver
        self.driver.maximize_window()
        self.action = worker.action
        self.config_action_chains()

    def config_action_chains(self):
        if self.with_action:
            action_chains = list()
            chain = self.chain_query
            for i in chain:
                tmp = ActionsHandler(self.action, self.driver, 
                                     i['chain'], i['chain_name'])
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
            content = content.text
        except Exception:
            tmp_worker = Worker(headless=True)
            driver = tmp_worker.driver
            driver.get(url)
            elem = driver.find_element_by_xpath("//*")
            content = elem.get_attribute("outerHTML")
            driver.quit()
        if dump:
            filename = "{}_{}".format(self.company_name,self.product_name) + ".txt"
            file_path = "{}/{}".format(HTML_LOCATION,filename)
            file_path = get_path(file_path)
            generate_file(file_path,content)
        else:
            return content

    @property
    def html_content(self):
        try:
            filename = "{}_{}".format(self.company_name,self.product_name) + ".txt"
            path = 'html_source/{}'.format(filename)
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
        self.check_html_changes()
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
             "driver": self.driver}
        for key, val in value.items():
            if key.lower() == 'attribute' or key.lower() == 'attributes':
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


def get_loaded(driver):
    script = "return document.readyState;"
    result=driver.execute_script(script)
    if result.lower() != 'complete':
        return get_loaded(driver)
    else:
        return