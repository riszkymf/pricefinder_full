from flask_restful import Resource, reqparse, request
from app.helpers.rest import response
from app.helpers import cmd_parser as cmd
from app import psycopg2,db
from app.libs import util as utils
from app.models import model



class VMDetails(Resource):

    def get(self):
        command = utils.get_command(request.path)
        command = "dt_"+command
        try:
            results = model.get_all(command)
            obj_userdata = list()
            for i in results:
                data = {
                    "id_vm": str(i['id_vm']),
                    "id_company_product": str(i['id_company_product']),
                    "spec_vcpu": i['spec_vcpu'],
                    'spec_clock': i['spec_clock'],
                    "spec_ram": i['spec_ram'],
                    "spec_os": i['spec_os'],
                    "spec_storage_volume": i['spec_storage_volume'],
                    'spec_ssd_volume': i['spec_ssd_volume'],
                    "spec_snapshot_volume": i['spec_snapshot_volume'],
                    "spec_template_volume": i['spec_template_volume'],
                    'spec_iso_volume': i['spec_iso_volume'],
                    "spec_public_ip": i['spec_public_ip'],
                    "spec_backup_storage": i['spec_backup_storage'],
                    'spec_price': i['spec_price'],
                    "spec_notes": i['spec_notes'],
                    "date_time": i['date_time']
                }
                obj_userdata.append(data)
        except Exception:
            results = None
        else:
            return response(200, data=obj_userdata)

    def post(self):
        json_req = request.get_json(force=True)
        command = utils.get_command(request.path)
        command = 'dt_'+command
        init_data = cmd.parser(json_req, command)
        respons = {}
        if init_data['action'] == 'insert':
            table = init_data['data'][0]['table']
            fields = init_data['data'][0]['fields']
            try:
                result = model.insert(table, fields)
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
                return response(200, data=fields , message=respons)
        if init_data['action'] == 'remove':
            table = ""
            tags = dict()
            fields = ""
            for i in init_data['data']:
                table = i['table']
                tags = i['tags']
            fields = str(list(tags.keys())[0])
            try:
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
        if init_data['action'] == 'view':
            obj_userdata = list()
            table = ""
            fields = None
            tags = dict()
            for i in init_data['data']:
                table = i['table']
                tags = i['tags']
                for a in tags:
                    if tags[a] is not None:
                        fields = a
            column = model.get_columns("v_product_vm")
            try:
                result = list()
                if fields is None:
                    query = """select * from v_product_vm"""
                    db.execute(query)
                    rows = db.fetchall()
                    for row in rows:
                        result.append(dict(zip(column, row)))
                else:
                    query = """ select * from v_product_vm_test where """+fields+"""='"""+tags[fields]+"""'"""
                    db.execute(query)
                    rows = db.fetchall()
                    for row in rows:
                        result.append(dict(zip(column, row)))
            except Exception as e:
                respons = {
                    "status": False,
                    "messages": str(e)
                }
            else:
                for i in result :
                    data = {
                    "id_company": str(i['id_company']),
                    "id_company_product": str(i['id_company_product']),
                    "id_product": str(i['id_product']),
                    'id_vm': str(i['id_vm']),
                    "id_additional_features": str(i['id_additional_features']),
                    "nm_company": i['nm_company'],
                    "url_company": i['url_company'],
                    'nm_company_product': i['nm_company_product'],
                    "nm_product": i['nm_product'],
                    "currency_used": i['currency_used'],
                    'spec_clock': i['spec_clock'],
                    "spec_ram": i['spec_ram'],
                    "spec_os": i['spec_os'],
                    'spec_storage_volume': i['spec_storage_volume'],
                    "spec_ssd_volume": i['spec_ssd_volume'],
                    "spec_snapshot_volume": i['spec_snapshot_volume'],
                    "spec_template_volume": i['spec_template_volume'],
                    'spec_iso_volume': i['spec_iso_volume'],
                    "spec_public_ip": i['spec_public_ip'],
                    "spec_backup_storage": i['spec_backup_storage'],
                    'spec_features': i['spec_features'],
                    "spec_features_value": i['spec_features_value'],
                    "spec_features_price": i['spec_features_price'],
                    'spec_price': i['spec_price'],
                    "date_time": i['date_time']

                    }
                    obj_userdata.append(data)
                respons = {
                    "status": True,
                    "messages": "Fine!"
                }
            finally:
                return response(200, data=obj_userdata , message=respons)

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
            except Exception as e:
                respons = {
                    "status": False,
                    "messages": str(e)
                }
            else:
                for i in result :
                    data = {
                    "id_vm": str(i['id_vm']),
                    "id_company_product": str(i['id_company_product']),
                    "spec_vcpu": i['spec_vcpu'],
                    'spec_clock': i['spec_clock'],
                    "spec_ram": i['spec_ram'],
                    "spec_os": i['spec_os'],
                    "spec_storage_volume": i['spec_storage_volume'],
                    'spec_ssd_volume': i['spec_ssd_volume'],
                    "spec_snapshot_volume": i['spec_snapshot_volume'],
                    "spec_template_volume": i['spec_template_volume'],
                    'spec_iso_volume': i['spec_iso_volume'],
                    "spec_public_ip": i['spec_public_ip'],
                    "spec_backup_storage": i['spec_backup_storage'],
                    'spec_price': i['spec_price'],
                    "spec_notes": i['spec_notes'],
                    "date_time": i['date_time']
                    }
                    obj_userdata.append(data)
                respons = {
                    "status": True,
                    "messages": "Fine!"
                }
            finally:
                return response(200, data=obj_userdata , message=respons)