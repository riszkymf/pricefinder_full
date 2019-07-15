from docopt import docopt
from crawler.libs import run
from crawler.libs import util
from .base import Base
import os

class Trial(Base):
    """
    Usage:
        trial (FILE) [options] [-dHp]

    Options:
    -h --help                   Print Usage
    FILE                        Crawler Configuration File
    -d Location                 Dump Data Location
    --ignore FILE               Ignore Crawler
    -H                          Headless
    -p                          Print obtained data
    """

    is_dumped = False
    is_headless = False
    dump_location=None
    is_printed=False
    
    def execute(self):
        files = list()
        ignore = list()
        if self.args['-d']:
            self.is_dumped = True
            self.dump_location = self.args['-d']
        if self.args['--ignore']:
            ignore_path = util.get_path(self.args['--ignore'])
            ignore = [ignore_path]
        
        self.is_headless = self.args['-H']
        self.is_printed = self.args['-p']

        files = self.args['FILE']

