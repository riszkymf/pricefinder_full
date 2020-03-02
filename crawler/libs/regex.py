import re
from crawler.libs import util

re = re

class RegexHandler(object):
    query = dict()
    method = None
    status = None
    
    def __init__(self,value,query):
        self.init_val = value
        self.re = re
        _query = query[0]
        self.register_aliases()
        for key,value in _query.items():
            try:
                parse_query = util.flatten_dictionaries(value)
            except Exception as e:
                print("Error Configuration")
                print(str(e))
                self.status = False
                return 0
            self.query = parse_query
            self.method = key
        self.status = True
            
    def __getvalue__(self):
        if self.status:
            func_dict = self.aliases
            func = func_dict[self.method]
            query = self.query
            value = self.init_val
            result = func(value,**query)
            return result
        else:
            return self.init_val
            
    def register_aliases(self):
        """To avoid simple error from yaml configuration, register possible aliases for regex method here"""
        aliases = {
            "findall" : self.findall,
            "find_all": self.findall,
            "search": self.search,
            "find_group": self.search,
            "sub": self.sub,
            "replace": self.sub,
            "match": self.match,
            "index": self.match
        }
        self.aliases = aliases

    def match(self, value, **query):
        re = self.re
        regex = query['regex']
        default = query.get("default_value",False)
        match_index = query["match_index"]
        try:
            _result = re.finditer(str(regex), repr(value))
            result = [ i.group() for i in list(_result)]
            if match_index:
                result_string = result[int(match_index)]
            else:
                result_string = " ".join(result)
        except Exception as e:
            print(str(e))
            if default:
                result_string = default
            else:
                result_string = value
        return result_string

    def findall(self,value,**query):
        re = self.re
        regex = query['regex']
        default = query.get("default_value",False)
        match_index = query['match_index']
        try:
            result=re.findall(str(regex),repr(value))
            if match_index:
                result_string = result[int(match_index)]
            else:
                result_string = " ".join(result)
        except Exception as e:
            print(str(e))
            if default:
                result_string = default
            else:
                result_string = value
        return result_string
    
    def search(self,value,**query):
        default = query.get("default_value",False)
        re = self.re
        regex = query['regex']
        try:
            result = re.search(regex,repr(value))
            _tmp_ = result.group(1)
            
            if not isinstance(_tmp_,str):
                result = _tmp_[0]
            else:
                result = _tmp_
            result_string = result
        except Exception as e:
            print(str(e))
            if default:
                result_string = default
            else:
                result_string = value
        return result_string
            
    def sub(self,value,**query):
        re = self.re
        default = query.get("default_value",False)
        regex = query['regex']
        repl = query.get('repl',query.get('replacement',query.get('replace',"")))
        try:
            result = re.sub(regex,repr(value))
            result_string = result
        except Exception as e:
            print(str(e))
            if default:
                result_string = default
            else:
                result_string = value
            
        return result_string