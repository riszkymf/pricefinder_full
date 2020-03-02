from flask_restful import Resource, reqparse, request
from app.helpers.rest import *
from app.middlewares.eshandler import *
from app.libs import es_query_builder
from app import es,logging

index = 'active_user'

class ActiveUsersAll(Resource):
    
    def get(self):
        try:
            results = scan_data(es,index)
        except Exception as e:
            logging.error(str(e))
            return response(404,str(e))
        else:
            results = [i['_source'] for i in results]
            return response(200, message="Success", data=results)

    def post(self):
        json_req = request.get_json(force=True)
        q_filter = json_req['filter']
        check = q_filter.get("field",False)
        if not check:
            q_filter['field'] = dict()
        filters = list()
        for key,val in q_filter.items():
            if key.lower() == 'date':
                q = es_query_builder.date_filter(val, date_field="date")
                filters.append(q)
            elif key.lower() == 'field':
                q = es_query_builder.match_query(val)
                filters.extend(q)
        
        query = es_query_builder.build_queries(filters)
        try:
            es_result = scan_data(es,index,query)
        except Exception as e:
            logging.error(str(e))
            return response(404,message=str(e))
        else:
            results = [i['_source'] for i in es_result]
            return response(200,message="Success",data=results)

class ActiveUsers(Resource):
    
    def get(self,product_name):
        try:
            query = [es_query_builder.match_query({"slug": product_name})]
            query = es_query_builder.build_queries(query)
            results = scan_data(es,index,search_query=query)
        except Exception as e:
            logging.error(str(e))
            return response(404,str(e))
        else:
            results = [i['_source'] for i in results]
            return response(200, message="Success", data=results)

    def post(self,product_name):
        json_req = request.get_json(force=True)
        q_filter = json_req['filter']
        check = q_filter.get("field",False)
        if not check:
            q_filter['field'] = dict()
        q_filter['field']['slug'] = product_name
        filters = list()
        for key,val in q_filter.items():
            if key.lower() == 'date':
                q = es_query_builder.date_filter(val, date_field="date")
                filters.append(q)
            elif key.lower() == 'field':
                q = es_query_builder.match_query(val)
                filters.extend(q)
        
        query = es_query_builder.build_queries(filters)
        try:
            es_result = scan_data(es,index,query)
        except Exception as e:
            logging.error(str(e))
            return response(404,message=str(e))
        else:
            results = [i['_source'] for i in es_result]
            return response(200,message="Success",data=results)