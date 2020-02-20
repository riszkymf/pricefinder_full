from docopt import docopt
from crawler.libs import run
from crawler.libs import util
from .base import Base
import os

class Trial(Base):
    """
    Usage:
        send_conf (FILE)

    Options:
    -h --help                   Print Usage
    FILE                        Crawler Configuration File
    """

    
    def execute(self):
        files = list()
        ignore = list()
        kwargs = dict()
        if self.args['-d']:
            self.is_dumped = True
            self.dump_location = self.args['-d']
        if self.args['--ignore']:
            ignore_path = util.get_path(self.args['--ignore'])
            ignore = [ignore_path]
        
        self.is_headless = self.args['-H']
        self.is_printed = self.args['-p']

        files = self.args['FILE']

        kwargs['force_dump'] = False
        kwargs['force_headless'] = True
        kwargs['dump_to_json'] = self.is_dumped

        result = run.run(**kwargs)

        