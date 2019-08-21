from ..libs.util import *
import re

def parser(json, command=None):
    sdl_endpoint = repodata()
    endpoint = sdl_endpoint['endpoint'][command]
    parameter_fix = list()
    key_query = None
    return_paramfix = list()
    for i in json:
        tagfields=dict()
        for parameters_key in endpoint[i]:
            try:
                parameters_check = json[i][parameters_key]
            except Exception:
                parameters_check = None
            if parameters_check:
                key_query = parameters_key
                data_variabel = dict()
                paramemeters_data = endpoint[i][parameters_key]
                for variabel_key in paramemeters_data: 
                    try:
                        variabel_check = json[i][parameters_key][variabel_key]
                        if 'regex' in paramemeters_data[variabel_key] and paramemeters_data[variabel_key]['regex']:
                            pattern = paramemeters_data[variabel_key]['regex']
                            isvalidated = validate_regex(pattern,variabel_check)
                            if not isvalidated:
                                print(json)
                                raise ValueError('Input does not match Regex Pattern')
                    except Exception:
                        variabel_check = None
                    if variabel_check:
                        data_variabel[variabel_key] = json[i][parameters_key][variabel_key]
                    else:
                        try:
                            data_variabel[variabel_key] = endpoint[i][parameters_key][variabel_key]['default']
                        except Exception as e:
                            print(str(e))
                            print(json)
                            print(variabel_key)
                    tagfields[parameters_key]=data_variabel
        parameter=dict()
        for key in tagfields:
            try:
                fields_check = tagfields["fields"]
            except Exception:
                fields_check = None

            try:
                tags_check = tagfields["tags"]
            except Exception:
                tags_check = None

            if fields_check is None and tags_check is not None:
                parameter = {
                    'table': command,
                    'tags' : tagfields['tags']
                }
            elif fields_check is not None and tags_check is None:
                parameter = {
                    'table': command,
                    'fields' : tagfields['fields']
                }
            elif fields_check is not None and tags_check is not None:
                parameter = {
                    'table': command,
                    'fields' : tagfields['fields'],
                    'tags' : tagfields['tags']
                }
            else:
                data = {
                    key_query : tagfields[key]
                }
                parameter = {
                    'table': command,
                    "query" : data,
                }

        parameter_fix.append(parameter)
        return_paramfix = {
            'action': i,
            'data': parameter_fix,
        }
    return return_paramfix


def validate_regex(pattern,value):
    try:
        result = re.match(pattern,value)
    except Exception as e:
        print(str(e))
    
    if result:
        return True
    else:
        print(value," Does not match regex")
        return False