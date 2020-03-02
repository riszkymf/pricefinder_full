import os,json,yaml,requests

from requests.exceptions import ConnectionError

from .base import Base

from crawler.libs.util import ROOT_PATH
from termcolor import colored

from elasticsearch import Elasticsearch

class Config(Base):
    """
    usage:
        config init
        config update
        config show
        config rm

    Options :
    -h --help                 Print usage
    init                      Create new configuration
    update                    Replace existing configuration
    show                      Show configuration detail
    rm                        Remove existing configuration


    Commands:
     config                     Configure crawler
    """
    


    def execute(self):
        _yes = ["y","yes"]
        _no = ["n","no"]

        print(self.args)
        path = os.path.join(ROOT_PATH,"crawler_init.json")
        _configuration = {
            "REMOTE_DRIVER" : "0",
            "REMOTE_HOST" : None,
            "REMOTE_PORT" : None,
            "CHROMEDRIVER_PATH": None,
            "ES_HANDLER" : None,
            "ES_INIT": None
        }
        if self.args["rm"]:
            try:
                os.remove(path)
            except FileNotFoundError:
                print(colored("crawler_init.json does not exists","red"))
                exit()
            except Exception as e:
                print(colord(str(e),"red"))
                exit()
            else:
                print(colored("Success!","green"))
                exit()
        elif self.args["show"]:
            try:
                with open(path,"r") as f:
                    config = f.read()
                    config = json.loads(config)
            except FileNotFoundError :
                print(colored("No configuration found","red"))
                exit()
            except Exception as e:
                print(colored(str(e),"red"))
                exit()
            else:
                print(json.dumps(config, indent=4))
                exit()
        elif self.args["update"]:
            msg_success = "Update success!"
            try:
                with open(path,"r") as f:
                    config = f.read()
                    config = json.loads(config)
            except FileNotFoundError :
                print(colored("No configuration found","red"))
                exit()
            except Exception as e:
                print(colored(str(e),"red"))
                exit()
        elif self.args["init"]:
            msg_success = "crawler_init.json is created"
            config = dict()

        _ans = input("Use remote webdriver ? (y/n) :")
        while _ans.lower() in _yes:
            _configuration["REMOTE_WEBDRIVER"]["REMOTE_DRIVER"] = "1"
            _host = input("REMOTE_HOST : ")
            _port = input("REMOTE_PORT : ")
            try:
                print(colored("Connecting to remote host...","yellow"))
                res = requests.get("http://{}:{}".format(_host,_port))
            except Exception as e:
                print(colored(str(e),"red"))
                _ans = input("Can not connect to remote webdriver. Try again ?")
            else:
                _configuration["REMOTE_WEBDRIVER"]["REMOTE_HOST"] = "http://"+_host
                _configuration["REMOTE_WEBDRIVER"]["REMOTE_PORT"] = _port
                break
        print("Type path for chromedriver (Leave empty for default)")
        
        _ans = input("CHROMEDRIVER_PATH : ")
        _configuration["CHROMEDRIVER_PATH"] = _ans
        _ans = input("Configure elasticsearch client ? (y/n/) : ")
        
        while _ans.lower() in _yes:
            _host = input("Elasticsearch Host : ")
            _init = input("Elasticsearch init : ")
            try:
                print(colored("Connecting to remote host...","yellow"))
                res = requests.get("{}".format(_host))
            except Exception as e:
                print(colored(str(e),"red"))
                _ans = input("Can not connect to elasticsearch client. Try again ?")
            else:
                _configuration["ELASTIC"]["ES_HANDLER"] = _host
                _configuration["ELASTIC"]["ES_INIT"] = _init
                break
        config.update(_configuration)
        with open(path,"w") as f:
            json.dump(config,f,ensure_ascii=False,indent=4)
        print(colored(msg_success,"green"))
        return


        

    @property
    def default_config(self):
        print(colored("Configuration is not set, using default configuration" , "yellow"))
        return os.path.join(ROOT_PATH,"es_index.yml")


