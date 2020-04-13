import os,json,yaml,requests,importlib,crawler

from .base import Base

from termcolor import colored

from elasticsearch import Elasticsearch
from app.middlewares.eshandler import *
from crawler.libs.util import ROOT_PATH

class CrawlerConfig(Base):
    """
    usage:
        config create CONFNAME FILEPATH
        config read CONFNAME
        config update CONFNAME
        config update CONFNAME -f FILEPATH
        config delete CONFNAME
        config -h 

    Options :
    -h --help                 Print usage
    CONFNAME                  Set Configuration name
    FILEPATH                  Path to configuration file

    Commands:
     config                     Scrape Data
    """
    


    def execute(self):

        print(self.args)
        ans = ['yes','y','n','no']
        act_list = ["create","read","update","delete"]
        for act in act_list:
            if self.args[act]:
                action = act

        config_exist = False

        conf_path = os.path.join(ROOT_PATH,"crawler_init.json")
        try:
            with open(conf_path,"r") as f:
                _init_conf = f.read()
                _init_conf = json.loads(_init_conf)
        except FileNotFoundError:
            print(colored("crawler_init.json not found","yellow"))
            _init_conf = dict()
        else:
            config_exist = True
            for key,val in _init_conf.items():
                os.environ[key] = val

        importlib.reload(crawler)

        from crawler import es,logging
        

        if action == 'create':
            path = os.path.join(os.getcwd(),self.args['FILEPATH'])
            try:
                with open(path,"r+") as f:
                    data = yaml.safe_load(f.read())
            except FileNotFoundError:
                print(colored("File not found: {}".format(path),"red"))
                return False

            url = [i for i in data[0]['config'] if 'base_url' in i.keys()]
            url = url[0]['base_url']
            data = {
                "config_name": self.args["CONFNAME"],
                "config_json": json.dumps(data),
                "url": url
            }
            res = es.index("crawler_config",body=data)
            print(res)
        elif action == 'read':
            query = {
                "match": {"config_name": self.args["CONFNAME"]}
            }
            res = scan_data(es,'crawler_config',search_query={"query": query})
            if len(res) == 0:
                print(colored("Configuration Not Found!!","yellow"))
                exit()
            res = res[0]['_source']['config_json']
            print(res)
        elif action == 'update':
            query = {
                "match": {"config_name": self.args["CONFNAME"]}
            }
            res = scan_data(es,'crawler_config',search_query={"query": query})
            if len(res) == 0:
                print(colored("Configuration Not Found!!","yellow"))
                exit()
            config_id = res[0]['_id']
            config_data = res[0]["_source"]
            if self.args['-f']:
                path = os.path.join(os.getcwd(),self.args['FILEPATH'])
                with open(path,"r+") as f:
                    json_conf = json.loads(yaml.safe_load(f.read()))
            else:
                data = {
                    "config_name": self.args["CONFNAME"],
                    "url": config_data.get("url",""),
                    "config_json": config_data["config_json"]
                }
                ans = input("Enter configuration name (Empty the value if name is not changed): ")
                if ans:
                    data["config_name"] = ans
                ans = input("Enter target url (Empty the value if name is not changed): ")
                if ans:
                    data["url"] = ans
                ans = input("Enter new configuration path (Empty the value if name is not changed): ")
                if ans:
                    try:
                        path = os.path.join(os.getcwd(),ans)
                        with open(path,"r+") as f:
                            yaml_data = yaml.safe_load(f.read())
                            json_conf = json.dumps(yaml_data)
                        data["config_json"] = json_conf
                    except FileNotFoundError:
                        print(colored("File not Found: {}".format(path),'red'))
                res = es.update(index="crawler_config",doc_type="_doc",id=config_id,body={"doc" : data})
                if res['result'] == 'updated':
                    print(colored("Success!","green"))
                else:
                    print(res)
                exit()