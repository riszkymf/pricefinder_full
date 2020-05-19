import os,json,sys
from pathlib import Path
from crawler.libs.run import CrawlerExecutor as CE
from crawler.libs.handler import ESDataSend,generate_id
from crawler.libs.util import dump_to_tmp,load_config
from crawler import logging

HEADLESS = os.getenv("HEADLESS",'0')
try:
    HEADLESS = bool(int(HEADLESS))
except ValueError :
    logging.ERROR("Headless Value must be either 0 or 1")
    HEADLESS = True


ROOT_PATH = os.path.abspath(Path(__file__).parent.parent)
TMP_DIR = os.path.join(ROOT_PATH,"tmp")

files = os.listdir(TMP_DIR)
files = [os.path.join(TMP_DIR,f) for f in files]
configs = list()
for f in files:
    f_name = f.split("/")[-1]
    if os.path.isfile(f) and f_name.startswith("cfg_"):
        try:
            with open(f,"r") as conf:
                _tmp = json.loads(conf.read())
        except Exception as e:
            logging.ERROR(str(e))
        else:
            configs.append(_tmp)

_config = {
    "force_dump": False,
    "stack_send": False
}
count = 0
# for f,cfg in zip(files, configs):
#     d = {"report":{ "status": "True"},
#         "data": dict()}
#     try:
#         c = CE(json_config=cfg,force_headless=True,**_config)
#         cfgs_ = c.crawler_configs
#         result = list()
#         config = c.scrape(cfgs_)
#         print(f)
#     except Exception as e:
#         logging.ERROR(str(e))

    