import os,logging
from datetime import date,datetime,timedelta
from glob import glob
from logging import Formatter,FileHandler

def create_logger(name,level=logging.INFO,logfile=None):
    if logfile == None:
        filename = name + '.log'
        filepath = '/../../log/' + filename
        filepath = os.path.abspath(os.path.dirname(__file__))+filepath
        logfile = os.path.abspath(filepath)
    if not os.path.isdir(os.path.dirname(logfile)):
        filename = name + '.log'
        filepath = '/' + filename
        filepath = os.path.abspath(os.path.dirname(__file__))+filepath
        logfile = os.path.abspath(filepath)

    loghandler = logging.getLogger(str(name))
    loghandler.setLevel(level)
    file_handler = FileHandler(logfile)
    file_handler.setLevel(level)
    file_handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    loghandler.addHandler(file_handler)

    return loghandler



def log_file_listing():
    filepath = os.path.abspath(os.path.abspath(os.path.dirname(__file__))+'/../../log')
    files = glob(filepath+'/odscron-*')
    now = datetime.now()
    now = now.date()
    offsetdate = now - timedelta(weeks=1)
    files = [(i.split('/')[-1],i) for i in files]
    file_remove = list()
    for i in files:
        date_time = i[0].split("-")
        date_time.pop(0)
        date_time = "-".join(date_time)
        date_time = date_time.replace(".log","")
        date_time = datetime.strptime(date_time,"%Y-%m-%d")
        if date_time.date() < offsetdate:
            file_remove.append(i[1])
    return file_remove

