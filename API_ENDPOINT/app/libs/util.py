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