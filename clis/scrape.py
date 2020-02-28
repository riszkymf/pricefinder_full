import os,json,yaml,importlib

from .base import Base
from termcolor import colored
import crawler
from crawler.libs.util import ROOT_PATH

def send_data(es_handler, datasets):
    try:
        res = es_handler.search(index="domain_type")
        domain_type = [i["_source"]["type"] for i in res["hits"]["hits"]]
    except Exception :
        domain_type = ['.id', '.com', '.xyz', '.net', '.org', '.co.id', '.web.id', '.my.id', '.biz.id', '.ac.id', '.sch.id', '.biz', '.co', '.tv', '.io', '.info']
    result = list()
    for i in datasets:
        if i['_index'] == 'domain':
            if i['nm_domain_type'].lower() not in domain_type:
                continue
        try:
            res = es_handler.index(index=i.pop("_index"),id=i.pop("_id"),body=i)
        except Exception as e:
            logging.error(str(e))
            print(str(e))
            res = {"status": False}
        result.append(res)
    return result

class Scrape(Base):
    """
    usage:
        scrape -f FILENAME ... [options] 
        scrape -e CONFIGNAME ... [options]
        scrape  -h | --help

    Options :
    -h --help                 Print usage
    -f FILENAME               Set Configuration File to Use
    -H --headless             Run on Headless WebDriver
    -r --remote               Run on Remote WebDriver
    -e CONFIGNAME             Use configuration on ESDB
    -d DUMPFILE               Dump Json Data to a file
    -s --send                 Send retrieved data to ESDB

    Commands:
     scrape                     Scrape Data
    """
    


    def execute(self):

        print(self.args)



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
        from crawler.libs.run import CrawlerExecutor as CE
        from crawler.libs.handler import ESDataSend,generate_id

        
        if self.args["-d"]:
            path = os.path.join(ROOT_PATH,self.args['-d'])
            try:
                with open(path,"w+") as f:
                    f.write("")
            except Exception as e:
                print(colored(str(e), "red"))
                exit()
        if self.args["--send"]:
            ES_CONFIG_PATH = os.getenv("ES_CONFIG_PATH", self.default_config)
            try:
                with open(ES_CONFIG_PATH,"r") as f:
                    es_init = f.read()
                    es_init = yaml.safe_load(es_init)
            except Exception as e:
                print(colored(str(e),"red"))
                exit()

            print(colored("Using ES Client at {}".format(os.getenv("ES_HANDLER")),"yellow"))
            
        
        if self.args["-f"]:
            json_config = list()
            for i in self.args["-f"]:
                path = os.path.join(ROOT_PATH,i)
                try:
                    with open(i,"r") as f:
                        _tmp = f.read()
                        _tmp = yaml.safe_load(_tmp)
                except Exception as e:
                    print(colored(str(e),"red"))
                    exit()
                else:
                    json_config.append(_tmp)

        elif self.args["-e"]:
            res = es.search(index="crawler_config", body={"query": {"match_all": {}}})
            res = res["hits"]["hits"]
            json_config = [json.loads(i["_source"]["config_json"]) for i in res if i["_source"]["config_name"] in self.args["-e"]]

        _config = {
            "force_dump" : False,
            "stack_send": False
        }           
        

        for configuration in json_config:
            bot = CE(json_config=configuration, force_headless=self.args["--headless"])
            cfgs = bot.crawler_configs
            result = list()
            bot.scrape(cfgs)
            print(colored("==================================== RESULT ====================================","green"))
            print(bot.flattened_data)
            if self.args["--send"]:
                esdata = ESDataSend(es,es_init,bot.flattened_data)
                tmp = list()
                for i in esdata.rawdata:
                    tmp.extend(esdata.compile_chunk_data(i))
                result = esdata.normalize(tmp)
                send_result = send_data(es,result)
                print(send_result)


    @property
    def default_config(self):
        print(colored("Configuration is not set, using default configuration" , "yellow"))
        return os.path.join(ROOT_PATH,"es_index.yml")