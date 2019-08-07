from flask_restful import Resource, reqparse, request
from app.helpers.rest import response
from app.helpers import cmd_parser as cmd
from app import psycopg2,db
from app.libs import util as utils
from app.models import model



class ConfigCrawler(Resource):
    
    def get(self):
        command = utils.get_command(request.path)
        command = "dt_"+command
        try:
            results = model.get_all(command)
            obj_userdata = list()
            for i in results:
                data = {
                    "id_conf": str(i['id_conf']),
                    "conf_nm": i['conf_nm']
                }
                obj_userdata.append(data)
        except Exception as e:
            results = None
        else:
            return response(200, data=obj_userdata)

    def post(self):
        json_req = request.get_json(force=True)
        command = utils.get_command(request.path)
        command = 'dt_'+command
        init_data = cmd.parser(json_req, command)
        respons = dict()
        if init_data['action'] == 'insert':
            data_conf = init_data['data'][0]['fields']['conf_data']
            conf_nm = init_data['data'][0]['fields']['conf_nm']
            date_time = init_data['data'][0]['fields']['date_time']
            data_filename = "{}.yaml".format(conf_nm)
            table = init_data['data'][0]['table']
            db_fields = {
                "conf_nm": conf_nm,
                "date_time": date_time
            }
            try:
                write = utils.dump_file(data_filename,data_conf)    
                result = model.insert(table, db_fields)
            except Exception as e:
                respons = {
                    "status": False,
                    "error": str(e)
                }
            else:
                respons = {
                    "status": True,
                    "messages": "Success",
                    "id": result
                }
            finally:
                return response(200, data=db_fields , message=respons)
        if init_data['action'] == 'remove':
            table = ""
            tags = dict()
            fields = ""
            for i in init_data['data']:
                table = i['table']
                tags = i['tags']
            fields = str(list(tags.keys())[0])
            try:
                row = model.get_by_id(table,fields,tags[fields])
                filename = row[0]['conf_nm']
                remove = utils.remove_config(filename)
                if remove:
                    result = model.delete(table, fields, tags[fields])
            except Exception as e:
                respons = {
                    "status": False,
                    "messages": str(e)
                }
            else:
                respons = {
                    "status": result,
                    "messages": "Success!"
                }
            finally:
                return response(200, data=tags, message=respons)

        if init_data['action'] == 'where':
            obj_userdata = list()
            table = ""
            fields = ""
            tags = dict()
            for i in init_data['data']:
                table = i['table']
                tags = i['tags']
                for a in tags:
                    if tags[a] is not None:
                        fields = a
            try:
                result = model.get_by_id(table,fields,tags[fields])
                f_name = result[0]['conf_nm']
                conf_data = utils.get_config(f_name)
            except Exception as e:
                respons = {
                    "status": False,
                    "messages": str(e)
                }
            else:
                for i in result :
                    data = {
                    "id_conf": str(i['id_conf']),
                    "conf_nm": i['conf_nm'],
                    'date_time': i['date_time'],
                    'conf_data': conf_data
                    }
                    obj_userdata.append(data)
                respons = {
                    "status": True,
                    "messages": "Fine!"
                }
            finally:
                return response(200, data=obj_userdata , message=respons)
