import json
import re

from bs4 import BeautifulSoup
from crawler.libs.util import get_page

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from crawler.libs.util import get_path,keypair_to_dict
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

base_url = 'https://account.zettagrid.id/'
company_name = 'zettagrid'
DRIVER_PATH = {"chrome": get_path('chromedriver'),
               "firefox": get_path('geckodriver')}
elementFilterTool = {"od": By.ID,
                     "xpath": By.XPATH,
                     "link_text": By.LINK_TEXT,
                     "partial_link_text": By.PARTIAL_LINK_TEXT,
                     "name": By.NAME,
                     "tag_name": By.TAG_NAME,
                     "class_name": By.CLASS_NAME,
                     "css_selector": By.CSS_SELECTOR}


class PricingSimulator(object):
    # TO DO, Set Up chromedrive on dotenv
    driverType = "chrome"
    driverPath = DRIVER_PATH['chrome']
    driver = None

    def __init__(self, *args, **kwargs):
        options = Options()
        options.headless = False
        self.driver = webdriver.Chrome(self.driverPath, options=options)
        self.action = ActionChains(self.driver)

    def parse_css_selector(self, css_selector):
        selectors = [i.rstrip(" ").lstrip(" ") for i in css_selector.split(">")]
        return selectors

    def dive(self, css_selector, object_):
        selectors = self.parse_css_selector(css_selector)
        for selector in selectors:
            object_ = getattr(object_, 'find_element_by_css_selector')(selector)
        return object_

    def get_price(self, element, text=None, attribute=None):
        if text:
            return element.text
        else:
            return element.get_attribute(attribute)

    def strtoint(self,value):
        if 'Rp' not in value:
            return float(value)
        else:
            number = re.sub("\D","",value)
            return float(number)

    def repeatable_action(self, object_, action, target=None, minVal=None, maxVal=None, cycle=None, timeout=100):
        try:
            cycle = range(minVal, maxVal)
        except:
            if cycle:
                cycle = range(0, cycle)
            else:
                cycle = range(0, 1)
        prices = list()
        for i in cycle:
            getattr(object_, str(action))(target)
            getattr(object_, 'perform')()
            d = self.watch_price(self.driver)
            prices.append(d)
        getattr(object_,'reset_actions')()
        return prices

    def extract_element(self, selectors, current_node=None):
        if not current_node:
            current_node = self.driver
        selector = selectors.pop(0)
        next_node = current_node.find_element_by_css_selector(selector)

        if len(selectors) > 0:
            return self.extract_element(selectors, next_node)
        else:
            return next_node

    def watch_price(self, driver=None):
        if not driver:
            driver = self.driver
        price_summary = 'html>body>div>#orderConfig>div.productsummary.sticky'
        price_content = self.dive(price_summary, driver)
        items = price_content.find_elements_by_xpath('//div[contains(@class,"text-left") and contains(@class,"summary_item")]')
        specs = [i for i in items]
        prices = price_content.find_elements_by_xpath('//div[contains(@class,"text-right") and contains(@class,"summary_item")]')
        price = [i for i in prices]
        d = {}
        for key, value in zip(specs, price):
            if key.text.strip(" ") and value.text.strip(" "):
                d[key.text] = value.text
        total_price = price_content.find_element_by_xpath('//span[@id="monthly_cost"]')
        d['total_price'] = total_price.text
        return d

class VirtualDataCenter(PricingSimulator):

    endpoint = 'catalog/product/configure/236/2'

    def __init__(self, *args, **kwargs):
        self.company_name = company_name
        super().__init__()
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self):
        self._url = base_url + self.endpoint
        self.driver.get(self._url)
        driver = self.driver
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "orderConfig"))
        )
        prices = self.simulate(driver=driver)
        self.save_data()
        self.processed_data = self.step_analyzer()
        return driver
        

    def simulate(self, driver=None):
        if not driver:
            driver = self.driver

        act = ActionChains(driver)
        product_area_selector = 'form#orderConfig>div.row>div#main_body'
        product_area = self.dive(product_area_selector, driver)

        compute_panel_selector = 'div#container_panel_compute_zone'
        compute_area = self.dive(compute_panel_selector, product_area)
        
        prices = list()

        storage_area_selector = 'div#container_panel_storage>div.panel-body'
        storage_area = self.dive(storage_area_selector, product_area)
        act.reset_actions()
        prices.append(self.watch_price())
        inputs_xpath = '//div[@class="panel-body"]/div[position()<5]//input'
        inputs = storage_area.find_elements_by_xpath(inputs_xpath)
        btn_up_xpath = '//div[@class="panel-body"]/div[position()<5]//div[contains(@class,"number-spin-btn-up")]'
        btn_ups = storage_area.find_elements_by_xpath(btn_up_xpath)

        for input_, btn_ in zip(inputs, btn_ups):
            act.move_to_element(input_)
            price = self.repeatable_action(act, 'context_click', cycle=1, target=btn_)
            prices += price
            act.reset_actions()
        select_area = driver.find_element_by_css_selector('select#option_821_zg-vdc-internet-access')
        selects = Select(select_area)

        index = len(selects.options)
        for i in range(0, index):
            selects.select_by_index(i)
            price = self.watch_price(self.driver)
            prices.append(price)
            sleep(0.05)


        self.prices = prices

        return prices

    def save_data(self):
        path = get_path('crawler/data/zettagrid_VirtualDataCenter.json')
        with open(path,'w+') as f:
            data = self.prices
            data = json.dumps(data)
            f.write(data)

    def rearrange_data(self, data):
        result = list()
        for row in data:
            d = {}
            for key, value in row.items():
                d__ = {}
                if "/" in key:
                    keys = key.split("/")
                    tmp = keys[0].split(" ")
                    d__ = {"amount": tmp[0],
                           "unit": tmp[1],
                           "price": value}
                    d[keys[1]] = d__
                else:
                    d[key] = {"price": value}
                if key is "total_price":
                    d['total_price'] = {"price": value}
            result.append(d)
        return result

    def step_analyzer(self,data=None):
        if not data:
            data = self.rearrange_data(self.prices)
        d = {}
        idx = len(data)
        for i in range(0,idx-1):
            for k1,v1,k2,v2 in zip(data[i].keys(),data[i].values(),data[i+1].keys(),data[i+1].values()):
                if v1 != v2 and k1 == k2:
                    key = k1.rstrip(" ").lstrip(" ")
                    diff_price = self.strtoint(v2['price']) - self.strtoint(v1['price'])
                    pricing = str(abs(diff_price))
                    if 'amount' in v1 and 'amount' in v2:
                        amount_diff = abs(self.strtoint(v2['amount']) - self.strtoint(v1['amount']))
                        amount = "/"+str(amount_diff)+v1['unit']
                    else:
                        amount = "None"
                    d[key] = {"pricing": pricing, "unit": amount}
                elif k2 not in data[i] and k2 is not "":
                    key = k2.rstrip(" ").lstrip(" ")
                    pricing = str(self.strtoint(v2['price']))
                    amount = "None"
                    d[key] = {"pricing": pricing, "unit": amount}
                elif k2 is "":
                    continue
        return d



class VirtualServer(PricingSimulator):

    endpoint = 'catalog/product/configure/230/3'

    def __init__(self, *args, **kwargs):
        self.company_name = company_name
        super().__init__()
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self):
        self._url = base_url + self.endpoint
        self.driver.get(self._url)
        driver = self.driver
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "orderConfig"))
        )
        prices = self.simulate(driver=driver)
        self.save_data()
        self.processed_data = self.step_analyzer()
        return driver
        
    def simulate(self, driver=None):
        if not driver:
            driver = self.driver

        act = ActionChains(driver)
        rows_xpath = "//div[@id='main_body']/div[@class='row'][position()<3]"
        panels_xpath = rows_xpath+"//div[contains(@class,'panel')]/div[@class='panel-body']"
        inputs_xpath = panels_xpath+"//input"
        btns_xpath = panels_xpath+"//div[contains(@class,'number-spin-btn-up')]"
        selects_xpath = panels_xpath+"//select"

        prices = list()
        prices.append(self.watch_price())

        inputs_ = driver.find_elements_by_xpath(inputs_xpath)
        btns = driver.find_elements_by_xpath(btns_xpath)
        selects = driver.find_elements_by_xpath(selects_xpath)

        for input_,btn_ in zip(inputs_,btns):
            act.move_to_element(input_)
            price = self.repeatable_action(act,'context_click',cycle=1,target=btn_)
            prices += price
            act.reset_actions()

        for select in selects:
            select_ = Select(select)
            index = len(select_.options)
            for i in range(0,index):
                select_.select_by_index(i)
                price = self.watch_price()
                prices.append(price)
                sleep(0.05)
        self.prices = prices
        return prices

    def save_data(self):
        path = get_path('crawler/data/zettagrid_VirtualServer.json')
        with open(path,'w+') as f:
            data = self.prices
            data = json.dumps(data)
            f.write(data)

    def rearrange_data(self, data):
        result = list()
        for row in data:
            d = {}
            for key, value in row.items():
                d__ = {}
                if "/" in key:
                    keys = key.split("/")
                    tmp = keys[0].split(" ")
                    d__ = {"amount": tmp[0],
                           "unit": tmp[1],
                           "price": value}
                    d[keys[1]] = d__
                else:
                    d[key] = {"price": value}
                if key is "total_price":
                    d['total_price'] = {"price": value}
            result.append(d)
        return result

    def step_analyzer(self,data=None):
        if not data:
            data = self.rearrange_data(self.prices)
        d = {}
        idx = len(data)
        for i in range(0,idx-1):
            for k1,v1,k2,v2 in zip(data[i].keys(),data[i].values(),data[i+1].keys(),data[i+1].values()):
                if v1 != v2 and k1 == k2:
                    key = k1.rstrip(" ").lstrip(" ")
                    diff_price = self.strtoint(v2['price']) - self.strtoint(v1['price'])
                    pricing = str(abs(diff_price))
                    if 'amount' in v1 and 'amount' in v2:
                        amount_diff = abs(self.strtoint(v2['amount']) - self.strtoint(v1['amount']))
                        amount = "/"+str(amount_diff)+v1['unit']
                    else:
                        amount = "None"
                    d[key] = {"pricing": pricing, "unit": amount}
                elif k2 not in data[i] and k2 is not "":
                    key = k2.rstrip(" ").lstrip(" ")
                    pricing = str(self.strtoint(v2['price']))
                    try:
                        amount = "/"+v2['amount']+v2['unit']
                    except:
                        amount = "None"
                    d[key] = {"pricing": pricing, "unit": amount}
                elif k2 is "":
                    continue
        return d

class VMBackup(PricingSimulator):

    endpoint = 'catalog/product/configure/240/20'

    def __init__(self, *args, **kwargs):
        self.company_name = company_name
        super().__init__()
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self):
        self._url = base_url + self.endpoint
        self.driver.get(self._url)
        driver = self.driver
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "orderConfig"))
        )
        prices = self.simulate(driver=driver)
        self.save_data()
        self.processed_data = self.step_analyzer()
        return driver
        
    def simulate(self, driver=None):
        if not driver:
            driver = self.driver

        act = ActionChains(driver)
        panels_xpath = "//div[contains(@class,'panel')]/div[@class='panel-body']"
        inputs_xpath = panels_xpath+'//input[contains(@class,"slider_input")]'
        btns_xpath = panels_xpath+"//div[contains(@class,'number-spin-btn-up')]"

        prices = list()
        prices.append(self.watch_price())

        inputs_ = driver.find_elements_by_xpath(inputs_xpath)
        btns = driver.find_elements_by_xpath(btns_xpath)

        for input_,btn_ in zip(inputs_,btns):
            act.move_to_element(input_)
            price = self.repeatable_action(act,'context_click',cycle=1,target=btn_)
            prices += price
            act.reset_actions()

        self.prices = prices
        return prices

    def save_data(self):
        path = get_path('crawler/data/zettagrid_VMBackup.json')
        with open(path,'w+') as f:
            data = self.prices
            data = json.dumps(data)
            f.write(data)

    def rearrange_data(self, data):
        result = list()
        for row in data:
            d = {}
            for key, value in row.items():
                d__ = {}
                if "/" in key:
                    if "gb" in key.lower():
                        d['Storage'] = {
                            "amount": key.split("/")[1].split(" ")[0],
                            "unit": "GB",
                            "price": value
                        }
                    else:
                        keys = key.split("/")
                        tmp = keys[1].split(" ")
                        d__ = {"amount": tmp.pop(0),
                               "unit": keys[0],
                               "price": value}
                        d[" ".join(tmp)] = d__
                if key is "total_price":
                    d['total_price'] = {"price": value}
            result.append(d)
        return result

    def step_analyzer(self,data=None):
        if not data:
            data = self.rearrange_data(self.prices)
        d = {}
        idx = len(data)
        for i in range(0,idx-1):
            for k1,v1,k2,v2 in zip(data[i].keys(),data[i].values(),data[i+1].keys(),data[i+1].values()):
                if v1 != v2 and k1 == k2:
                    
                    key = k1.rstrip(" ").lstrip(" ")
                    diff_price = self.strtoint(v2['price']) - self.strtoint(v1['price'])
                    pricing = str(abs(diff_price))
                    if 'amount' in v1 and 'amount' in v2:
                        amount_diff = abs(self.strtoint(v2['amount']) - self.strtoint(v1['amount']))
                        amount = "/"+str(amount_diff)+" "+v1['unit']
                    else:
                        amount = "None"
                    d[key] = {"pricing": pricing, "unit": amount}
                elif k2 not in data[i] and k2 is not "":
                    key = k2.rstrip(" ").lstrip(" ")
                    pricing = str(self.strtoint(v2['price']))
                    try:
                        amount = "/"+int(v2['amount'])+" "+v2['unit']
                    except:
                        amount = "None"
                    d[key] = {"pricing": pricing, "unit": amount}
                elif k2 is "":
                    continue
        return d

    def watch_price(self, driver=None):
        if not driver:
            driver = self.driver
        price_selector = 'html>body>div>#orderConfig>div.productsummary.sticky'
        price_content = self.dive(price_selector, driver)
        price_summary = driver.find_elements_by_xpath("//div[contains(@class,'productsummary')]//span[@class='summary_item'][position()<5]")
        subtitle_xpath = 'preceding-sibling::span[@class="summarysubtitle"][1]'
        content = [(i,i.find_element_by_xpath(subtitle_xpath)) for i in price_summary]
        tmp = [k.text+"/"+i.text for i,k in content]
        prices = map(lambda a: "Rp"+a.split("Rp")[-1], tmp)
        keys = map(self.get_keys, tmp)
        d = {}
        for key, value in zip(keys, prices):
            if key.strip(" ") and value.strip(" "):
                d[key.replace("\n","")] = value
        total_price = price_content.find_element_by_xpath('//span[@id="monthly_cost"]')
        d['total_price'] = total_price.text
        return d
    
    def get_keys(self, key):
        key = key.split("Rp")
        key.pop(-1)
        return "".join(key)