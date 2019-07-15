from bs4 import BeautifulSoup
from crawler.libs.util import get_page, get_path, get_rawpage
import requests
import yaml

base_url = 'https://developers.whatismybrowser.com/useragents/explore/software_name/'



class UserAgent(object):
    endpoint = ''
    browser = ''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except:
                print("Can not set value")
                pass    

    def run(self):
        self.url = base_url+self.endpoint
        result = get_rawpage(self.url)
        self.status_code = result.status_code
        data = self.soup_parser(result)
        self.data = data
        return data

    def soup_parser(self, result):
        page = result.text
        res = BeautifulSoup(page, "html.parser")
        table = res.find('table', class_='table-useragents')
        rows = table.find('tbody').find_all('td', class_='useragent')
        user_agent = [row.text for row in rows]
        return {self.browser: user_agent}

def generate_useragents():
    browserList = ['firefox', 'chrome', 'opera', 'safari']

    write_data = {}
    for browser in browserList:
        args = {'endpoint': browser, 'browser': browser}
        tmp = UserAgent(**args)
        d = tmp.run()
        write_data = {**write_data, **d}
    path = get_path('crawler/static/useragent.yaml')
    with open(path, 'w') as f:
        yaml.dump(write_data, f)
