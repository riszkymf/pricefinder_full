from bs4 import BeautifulSoup
from crawler.libs.util import get_page
import requests
import unicodedata


base_url = 'http://www.domainesia.com'
company_name = 'domainesia'


class VM(object):
    endpoint = '/vm/'
    product_name = 'VM'

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
        details = res.find_all('div', class_='pricingTable')
        result_data = []
        for detail in details:
            d = {}
            items = detail.find_all('li')
            for item in items:
                value = item.text
                value = unicodedata.normalize("NFKD", value)
                value = value.split(" ")
                key = value.pop(-1)
                d[key] = " ".join(value).rstrip(" ").lstrip(" ")
            d['duration'] = detail.find('h2').find('span').text
            price = detail.find('h2').text
            d['price'] = price.replace(d.get('duration', ''), '')
            result_data.append(d)
        return result_data


class Hosting(object):

    endpoint = '/hosting/'
    product_name = 'Hosting'

    def __init__(self, **kwargs):
        self.company_name = company_name
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass

    def run(self, id_content):
        self.url = base_url + self.endpoint
        result = get_page(self.url)
        self.status_code = result.status_code
        data = self.soup_parser(result, id_content)
        self.data = data

    def soup_parser(self, result, id_content='techHosting'):
        page = result.text
        res = BeautifulSoup(page, "html.parser")
        data = res.find('div', id=id_content)
        table = data.find('table', class_='desktopElement')
        head = [i.text for i in table.find_all('th')]
        head.pop(0)
        result_data = [{'type': i} for i in head]

        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cell = row.find_all('td')
            key = cell.pop(0).text
            colspan = 0
            index = 0
            for item in cell:
                if item.get('colspan') is '5':
                    continue
                elif not item.get('colspan', False):
                    if item.text:
                        result_data[index][key] = item.text
                    else:
                        if 'check' in item.div['class']:
                            result_data[index][key] = "Yes"
                        else:
                            result_data[index][key] = "No"
                    index += 1
                else:
                    colspan = int(item.get('colspan'))
                    for i in range(0, colspan):
                        result_data[index][key] = item.text
                        index += 1
        return result_data

# Remove this later, handle on init


class RegularHosting(Hosting):
    product_type = 'Standard Hosting'
    id_content = 'techHosting'

    def run(self):
        super().run(self.id_content)


class BisnisHosting(Hosting):
    product_type = 'Bisnis Hosting'
    id_content = 'techHostingBisnis'

    def run(self):
        super().run(self.id_content)


class Domain(object):
    product_name = 'Domain'
    endpoint = '/harga-domain/'

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
        tables = res.find_all('table')
        keys = ["Domain", "Daftar", "Transfer", "Perpanjang"]
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cell = row.find_all_next('td', limit=4)
                d = {}
                for key, value in zip(keys, cell):
                    d[key] = value.get_text(strip=True)
                result_data.append(d)
        return result_data

