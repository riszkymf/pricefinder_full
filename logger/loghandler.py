import os,logging
from datetime import date,datetime
from logging import Formatter,FileHandler

def create_logger(name,level=logging.INFO,logfile=None):
    if logfile == None:
        filename = name + '.log'
        filepath = '../log/' + filename
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
