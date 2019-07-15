import yaml
import os
import sys
import json
import requests
import hashlib
import random

from os import listdir
from os.path import isfile,isdir,join,abspath

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
    root = os.getcwd()
    root = os.path.abspath(root+'/..')
    dir_ = root + '/conf'
    return dir_
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
        os.mkdir(dir_)
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
