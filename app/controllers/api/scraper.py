from flask_restful import Resource, reqparse, request
from app.helpers.rest import *
from app.middlewares.eshandler import *
from app.libs import es_query_builder
from app.libs.datahandler import get_date_reference,ES_CONF
from app import es,logging



class Scrape(Resource):
    
    def get(self,product_name):
        try:
            query = [es_query_builder.match_query({"_parent_index": product_name})]
            query = es_query_builder.build_queries(query)
            additional_results = scan_data(es,'additional_features',query)
            product_results = scan_data(es,product_name)
        except Exception as e:
            logging.error(str(e))
            return response(404,str(e))
        else:
            additional_results = [i['_source'] for i in additional_results]
            for i in product_results:
                i['_source']['additional_features'] = dict()
                for j in additional_results:
                    if i['_id'] == j['_parent_id']:
                        i['_source']['additional_features'].update(j)
            results = list()
            for i in product_results:
                tmp = dict()
                tmp["_id"] = i["_id"]
                tmp.update(i["_source"])
                results.append(tmp)
            return response(200, message="Success", data=results)

    def post(self,product_name):
        json_req = request.get_json(force=True)
        q_filter = json_req['filter']
        check = q_filter.get("field",False)
        if not check:
            q_filter['field'] = dict()
        filters = list()
        for key,val in q_filter.items():
            if key.lower() == 'date':
                q = es_query_builder.date_filter(val)
                filters.append(q)
            elif key.lower() == 'field':
                q = es_query_builder.match_query(val)
                filters.extend(q)
        query = es_query_builder.build_queries(filters)
        try:
            additional_query = [es_query_builder.match_query({"_parent_index": product_name})]
            additional_query = es_query_builder.build_queries(additional_query)
            additional_results = scan_data(es,'additional_features',additional_query)
            product_results = scan_data(es,product_name,query)
            additional_results = [i['_source'] for i in additional_results]
            for i in product_results:
                i['_source']['additional_features'] = dict()
                for j in additional_results:
                    if i['_id'] == j['_parent_id']:
                        i['_source']['additional_features'].update(j)
            results = list()
            for i in product_results:
                tmp = dict()
                tmp["_id"] = i["_id"]
                tmp.update(i["_source"])
                results.append(tmp)
        except Exception as e:
            logging.error(str(e))
            return response(404,message=str(e))
        else:
            return response(200,message="Success",data=results)