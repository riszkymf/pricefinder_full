from flask_restful import Resource, reqparse, request
from app.helpers.rest import response
from app.helpers import cmd_parser as cmd
from app import psycopg2,db
from app.libs import util as utils
from app.models import model



class HostingDetails(Resource):

    def get(self):
        command = utils.get_command(request.path)
        command = "dt_"+command
        try:
            results = model.get_all(command)
            obj_userdata = list()
            for i in results:
                data = {
                    "id_hosting": str(i['id_hosting']),
                    "id_company_product": str(i['id_company_product']),
                    'spec_price': i['spec_price'],
                    "spec_storage": i['spec_storage'],
                    'spec_database': i['spec_database'],
                    "spec_free_domain": i['spec_free_domain'],
                    "spec_hosting_domain": i['spec_hosting_domain'],
                    'spec_subdomain': i['spec_subdomain'],
                    "spec_ftp_user": i['spec_ftp_user'],
                    "spec_control_panel": i['spec_control_panel'],
                    'spec_email_account': i['spec_email_account'],
                    "spec_spam_filter": i['spec_spam_filter'],
                    "date_time": i['date_time']
                }
                obj_userdata.append(data)
        except Exception as e:
            print(str(e))
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
                    "id_hosting": str(i['id_hosting']),
                    "id_company_product": str(i['id_company_product']),
                    'spec_price': i['spec_price'],
                    "spec_storage": i['spec_storage'],
                    'spec_database': i['spec_database'],
                    "spec_free_domain": i['spec_free_domain'],
                    "spec_hosting_domain": i['spec_hosting_domain'],
                    'spec_subdomain': i['spec_subdomain'],
                    "spec_ftp_user": i['spec_ftp_user'],
                    "spec_control_panel": i['spec_control_panel'],
                    'spec_email_account': i['spec_email_account'],
                    "spec_spam_filter": i['spec_spam_filter'],
                    "date_time": i['date_time']                    }
                    obj_userdata.append(data)
                respons = {
                    "status": True,
                    "messages": "Fine!"
                }
            finally:
                return response(200, data=obj_userdata , message=respons)
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
            column = model.get_columns("v_product_hosting")
            column_additional_features = model.get_columns("dt_additional_features")
            try:
                result = list()
                result_additional_features = list()
                if fields is None:
                    query = """select * from v_product_hosting"""
                    db.execute(query)
                    rows = db.fetchall()
                    for row in rows:
                        result.append(dict(zip(column, row)))
                else:
                    query = """ select * from v_product_hosting where """+fields+"""='"""+tags[fields]+"""'"""
                    db.execute(query)
                    rows = db.fetchall()
                    for row in rows:
                        result.append(dict(zip(column, row)))
                query = """ select * from dt_additional_features where id_hosting is not null"""
                db.execute(query)
                rows = db.fetchall()
                for row in rows:
                    result_additional_features.append(dict(zip(column_additional_features,row)))
            except Exception as e:
                respons = {
                    "status": False,
                    "messages": str(e)
                }
            else:
                for i in result :
                    data_additional_features = list()
                    for row in result_additional_features:
                        if row['id_hosting'] == i['id_hosting']:
                            data_additional_features.append(row)
                    data = {
                    "id_company": str(i["id_company"]),
                    "id_product": str(i["id_product"]),
                    "id_hosting": str(i['id_hosting']),
                    "id_company_product": str(i['id_company_product']),
                    "nm_company": i['nm_company'],
                    "url_company": i['url_company'],
                    "nm_product": i['nm_product'],
                    "nm_company_product": i['nm_company_product'],
                    "spec_storage": i['spec_storage'],
                    'spec_price': i['spec_price'],
                    "spec_storage": i['spec_storage'],
                    'spec_database': i['spec_database'],
                    "spec_free_domain": i['spec_free_domain'],
                    "spec_hosting_domain": i['spec_hosting_domain'],
                    'spec_subdomain': i['spec_subdomain'],
                    "spec_ftp_user": i['spec_ftp_user'],
                    "spec_control_panel": i['spec_control_panel'],
                    'spec_email_account': i['spec_email_account'],
                    "spec_spam_filter": i['spec_spam_filter'],
                    "date_time": i['date_time'],
                    "additional_features": data_additional_features
                    }
                    obj_userdata.append(data)
                respons = {
                    "status": True,
                    "messages": "Fine!"
                }
            finally:
                return response(200, data=obj_userdata , message=respons)
