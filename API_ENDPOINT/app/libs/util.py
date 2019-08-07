import yaml
import os
import sys
import json
import requests
import hashlib
import random

from os import listdir
from os.path import isfile,isdir,join,abspath
from app.configs import APP_ROOT
from dotenv import load_dotenv

ENV_PATH = os.path.abspath(os.path.join(os.path.abspath(APP_ROOT),'../.env'))
load_dotenv(dotenv_path=ENV_PATH)
CONF_PATH = os.getenv("CRAWLER_CONFIGURATION_PATH")
DUMP_LOCATION = os.getenv("DATA_DUMP_LOCATION")
HTML_LOCATION = os.getenv("HTML_CONTENT_DUMP_LOCATION")

def create_dir(path):
    try:
        os.mkdir(path)
    except FileNotFoundError:
        head = os.path.split(path)[0]
        tail = os.path.split(path)[1]
        create_dir(head)
        return create_dir(path)
    except FileExistsError:
        return path
    except Exception as e:
        print(e)
        return False
    finally:
        return path

def create_confdir(CONF_PATH=CONF_PATH,DUMP_PATH=DUMP_LOCATION,HTML_PATH=HTML_LOCATION):
    CONF_DIR = [CONF_PATH,DUMP_LOCATION,HTML_LOCATION]
    for path in CONF_DIR:
        check=create_dir(path)
    if not check:
        print("Creating Directory Failed")

def load_yaml(filename):
    with open(filename, "r") as f:
        data = yaml.safe_load(f)
        f.close()
    return data

def repodata():
    path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'templates/db.yaml'))
    d=load_yaml(path)
    return d

def get_path(path):
    cwd = os.getcwd()
    new_path = os.path.join(cwd, path)
    new_path = os.path.abspath(new_path)
    return new_path

def get_all(folder, ignores=list()):
    if not os.path.isabs(folder):
        folder = get_path(folder)
    if ignores:
        for i in ignores:
            if not os.path.isabs(i):
                i = get_path(i)
    files = list()
    dirs = [folder]
    ext = ['yaml','yml']

    def dive(f_data):
        if len(dirs) > 0:
            for d_dir in f_data:
                for d in listdir(d_dir):
                    path = join(d_dir, d)
                    if check_exist(path):
                        if isdir(path) and path not in ignores:
                            dirs.append(path)
                        if isfile(path) and path not in ignores:
                            files.append(path)
                dirs.remove(d_dir)
                break
            return dive(dirs)
    dive(dirs)
    return files
    
def check_exist(path):
    return os.path.exists(path)

def collect_yaml_resource(folder):
    ext = ['yaml', 'yml']
    files_all = [f for f in listdir if isfile(join(folder, f))]
    return files_all

def get_config(conf_nm):
    f_name = conf_nm+'.yaml'
    root = get_conf_path()
    f_path = "{}/{}".format(root,f_name)
    try:
        data=load_yaml(f_path)
    except Exception as e:
        data = str(e)
    return data

def get_command(req):
    command = req.split("/")
    command = command[2]
    return command

def get_tag():
    id_ = hashlib.md5(str(timeset()).encode('utf-8')).hexdigest()
    return id_

def field_cleanup(data):
    d = {}
    for key,val in data.items():
        if val:
            d[key] = val
    return d

def remove_config(filename):
    filename = filename+'.yaml'
    root = get_conf_path()
    filepath = "{}/{}".format(root,filename)
    check = check_exist(filepath)
    if not check:
        return True
    else:
        try:
            os.remove(filepath)
        except Exception as e:
            print(str(e))
            return False
        else:
            return True

def get_conf_path():
    return CONF_PATH

def dump_file(filename,data):
    dir_ = get_conf_path()
    check_1 = os.path.exists(dir_)
    check_2 = os.path.isdir(dir_)
    check_value = check_1 and check_2
    file_path = dir_+'/'+filename
    if check_value:
        with open(file_path,'w+') as f:
            try:    
                yaml.dump(data,stream=f,default_flow_style=False)
                return True
            except yaml.YAMLError as e:
                print(str(e))
                return False
    else:
        create_confdir()
        dump_file(file_path,data)

def flatten_dictionaries(input_):
    output = dict()
    try:
        if isinstance(input_, list):
            for map_ in input_:
                output.update(map_)
        else:  # Not a list of dictionaries
            output = input_
    except Exception as e:
        return False
    else:
        return output
