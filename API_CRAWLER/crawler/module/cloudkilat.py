from bs4 import BeautifulSoup
from crawler.libs.util import get_page


base_url = 'http://www.cloudkilat.com'
company_name = 'cloudkilat'


class VM(object):
    endpoint = '/layanan/kilat-vm-2.0#harga'
    product_name = "VM 2.0"
    
    def __init__(self, **kwargs):
        self.company_name = company_name
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass    

    def run(self):
        self.url = base_url+self.endpoint
        result = get_page(self.url)
        self.status_code = result.status_code
        data = self.soup_parser(result)
        self.data = data

    def soup_parser(self, result):
        page = result.text
        res = BeautifulSoup(page, "html.parser")

        items = res.find_all("li", class_="item-none")
        result_data = []
        for item in items:
            d = {}
            if 'list-header' not in item['class']:
                d['Type'] = item.h4.text
                d['Duration'] = item.find('div', class_='duration').get_text(strip=True).replace(" ","").replace("\n"," ")
                specs = item.find('div', class_='spesifications')
                specs_details = specs.find_all('div', class_='value')
                for key, value in zip(header, specs_details):
                    d[key] = value.get_text(strip=True)
                d['price'] = item.h5.text
                d['notes'] = item.find('div', class_='notes').text
                result_data.append(d)
            else:
                header = [i.get_text(strip=True).replace(" ","_") for i in item.find_all('div',class_='item')]
        return result_data


class ObjectStorage(object):
    endpoint = "/layanan/kilat-storage#harga"
    product_name = "Object Storage"

    def __init__(self, **kwargs):
        self.company_name = company_name
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self):
        self.url = base_url + self.endpoint
        result = get_page(self.url)
        self.status_code = result.status_code
        data = self.soup_parser(result)
        self.data = data

    def soup_parser(self, result):
        page = result.text
        res = BeautifulSoup(page, "html.parser")
        price_area = res.find('ul', class_="price-list")
        items = price_area.find_all('li', class_='item-none')
        result_data = list()
        for item in items:
            d = {}
            d['Type'] = item.find('h4', class_='type').text
            d['Duration'] = item.find('div', class_='duration').get_text(strip=True).replace(" ","").replace("\n"," ")
            specs = zip(item.select("div.columns.item"),item.select("div.columns.value"))
            for key, value in specs:
                key = key.get_text(strip=True)
                value = value.get_text(strip=True)
                d[key] = value
            d['Price'] = item.find('h5', class_='price').text
            result_data.append(d)
        return result_data



class Plesk(object):
    endpoint = "/layanan/kilat-plesk#harga"
    product_name = "Plesk"

    def __init__(self, **kwargs):
        self.company_name = company_name
        for key,value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self):
        self.url = base_url + self.endpoint
        result = get_page(self.url)
        self.status_code = result.status_code
        data = self.soup_parser(result)
        self.data = data

    def soup_parser(self, result):
        page = result.text
        res = BeautifulSoup(page, "html.parser")
        price_area = res.find('ul', class_="price-list")
        items = price_area.find_all('li', class_='item-none')
        result_data = list()
        for item in items:
            d = {}
            d['duration'] = item.find('div',class_='duration').get_text(strip=True).replace(" ","").replace("\n"," ")
            specs = zip(item.select("div.columns.item"),item.select("div.columns.value"))
            for key, value in specs:
                key = key.get_text(strip=True)
                value = value.get_text(strip=True)
                d[key] = value
            d['price'] = item.find('h5', class_='price').text
            result_data.append(d)
        return result_data


class Hosting(object):
    endpoint = '/layanan/kilat-hosting'
    product_name = "hosting"

    def __init__(self, **kwargs):
        self.company_name = company_name
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self):
        self.url = base_url + self.endpoint
        result = get_page(self.url)
        self.status_code = result.status_code
        data = self.soup_parser(result)
        self.data = data

    def soup_parser(self, result):
        page = result.text
        res = BeautifulSoup(page, "html.parser")
        result_data = list()
        d = {}
        price_area = res.find('div', class_='pricing')
        d['duration'] = price_area.find('div', class_='duration').get_text(strip=True).replace(" ", "").replace("\n"," ")
        d['price'] = price_area.find('h1', class_='price').text
        
        features = res.find('div', class_='summary')
        features = features.find('ul')
        features_str = []
        items = features.find_all('li')
        for item in items:
            txt = item.text.replace('\n',' ').rstrip(' ').lstrip(' ')
            features_str.append(txt)
        d['features'] = features_str
        result_data.append(d)
        return result_data


class KilatIron(object):
    endpoint = '/layanan/kilat-iron'
    product_name = "Iron"

    def __init__(self, **kwargs):
        self.company_name = company_name
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self):
        self.url = base_url + self.endpoint
        result = get_page(self.url)
        self.status_code = result.status_code
        data = self.soup_parser(result)
        self.data = data

    def soup_parser(self, result):
        page = result.text
        res = BeautifulSoup(page, "html.parser")
        result_data = list()
        d = {}
        price_area = res.find('div', class_='pricing')
        d['duration'] = price_area.find('div', class_='duration').get_text(strip=True).replace(" ", "").replace("\n"," ")
        d['price'] = price_area.find('h1', class_='price').text
        features = res.find('div', class_='summary')
        features = features.find('ul')
        features_str = []
        items = features.find_all('li')
        for item in items:
            txt = item.text.replace('\n', ' ').rstrip(' ').lstrip(' ')
            features_str.append(txt)
        d['features'] = features_str
        result_data.append(d)
        return result_data


class Domain(object):
    endpoint = '/layanan/kilat-domain'
    product_name = "domain"

    def __init__(self, **kwargs):
        self.company_name = company_name
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self):
        self.url = base_url + self.endpoint
        result = get_page(self.url)
        self.status_code = result.status_code
        data = self.soup_parser(result)
        self.data = data

    def soup_parser(self, result):
        result_data = list()
        page = result.text
        res = BeautifulSoup(page, "html.parser")
        table = res.find('table', class_='price-table').find('tbody')
        keys = ["domain", "baru", "perpanjang", "harga"]
        rows = table.find_all('tr')
        for row in rows:
            d = {}
            cells = row.find_all('td')
            for key, value in zip(keys, cells):
                d[key] = value.text
            result_data.append(d)
        return result_data
