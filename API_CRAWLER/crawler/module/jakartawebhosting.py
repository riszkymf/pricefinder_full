from bs4 import BeautifulSoup
from crawler.libs.util import get_page
import requests
import unicodedata



base_url = 'https://www.jakartawebhosting.com'        
company_name = 'jakartawebhosting'


class CloudServer(object):
    endpoint = '/cloud-server/personal-cloud'
    product_name = 'Personal Cloud'

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
        self.product_name = title
        h2 = res.find_all('h2')
        for h in h2:
            if 'cloud server business' in h.text.lower():
                h2 = h
                break
        table = h2.find_next('table')
        rows = table.find_all('tr')
        headers = rows.pop(0)
        head = [i.get_text(strip=True) for i in headers.find_all('td')]
        head.pop(0)
        result_data = [{'Type': i} for i in head]

        for row in rows:
            cell = row.find_all('td')
            index = 0
            key = cell.pop(0).get_text(strip=True)
            if not key:
                continue
            for item in cell:
                if not item.get('colspan', False):
                    if 'select' in [i.name for i in item.descendants]:
                        opt = item.find_all('option')
                        d = []
                        for o in opt:
                            d.append(o.text)
                        result_data[index][key] = ','.join(d)
                    else:
                        result_data[index][key] = item.text
                    index += 1
        return result_data


class DedicatedServer(object):
    endpoint = '/dedicatedserver'
    product_name = "Dedicated Server" 

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
        soup = BeautifulSoup(page, 'html.parser')
        
        title = soup.find('div', class_='page_title').find('div',class_='title').text
        self.product_name = title
        main_content = soup.find('div', class_='hosting_page_plan_main')
        ul_items = main_content.find_all('ul')
        head = ul_items.pop(0)
        head = [li.text for li in head.find_all('li')]
        head[0] = "Type"
        result_data = list()
        for column in ul_items:
            d = {}
            li = column.find_all('li')
            for key, value in zip(head, li):
                if key and value.text:
                    if 'select' in [i.name for i in value.descendants]:
                        opt = value.find_all('option')
                        tmp = []
                        for o in opt:
                            tmp.append(o.text)
                        d[key] = ', '.join(tmp)
                    else:
                        d[key] = value.text
                elif value.find('i'):
                    d[key] = "Yes" if 'fa-check' in value.i['class'] else "No"
            result_data.append(d)
        return result_data


class Domain(object):
    endpoint = '/domainname/'
    product_name = "Domain Name" 

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
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find('div',id='maincontent')
        tables = div.find_all('table')
        tables.pop(-1)
        tables.pop(0)
        header = ['Domain', 'Harga']
        data_result = list()
        for table in tables:
            rows = table.find_all('tr')
            rows.pop(0)
            for row in rows:
                cells = row.find_all('td')
                d = {}
                for key, val in zip(header, cells):
                    if val.find('div'):
                        d[key] = val.find('div', class_='new-price').text
                    else:
                        d[key] = val.text
                data_result.append(d)
        return data_result


BusinessCloudServer = CloudServer(endpoint='/cloud-server/business-cloud')
PersonalCloudServer = CloudServer()
ServerUS = DedicatedServer(endpoint='/dedicatedserverus')
ServerSG = DedicatedServer(endpoint='/dedicatedserversg')
ServerID = DedicatedServer()
HostingLinuxPersonal = DedicatedServer(endpoint='/linuxhosting/linuxpersonalplans')
HostingLinuxBisnis = DedicatedServer(endpoint='/linuxhosting/linuxbusinessplans')
HostingWindowsPersonal = DedicatedServer(endpoint='/windowshosting/windowspersonalplans')
HostingWindowsBisnis = DedicatedServer(endpoint='/windowshosting/windowsbusinessplans')
HostingWordpress = DedicatedServer(endpoint='/wordpress-plan/')
HostingResellerLinux = DedicatedServer(endpoint='/reseller/reseller-linux-hosting-plans')
HostingResellerWindows = DedicatedServer(endpoint='/reseller/reseller-windows-hosting-plans')