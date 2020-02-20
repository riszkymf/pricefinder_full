import datetime
import json
import hashlib



time_format = "%Y-%m-%d"

def normalize(raw_data):
    _id_dict = {
        "date_created": raw_data["date_created"].strftime(time_format),
        "account_id": raw_data["account_id"],
        "event": raw_data["event"],
        "slug": raw_data["slug"]
    }
    _id_json = json.dumps(_id_dict)
    _id = hashlib.md5(_id_json.encode('utf8')).hexdigest()
    prep_data = {
        "date": raw_data["date"].strftime("%Y-%m-%d %H:%M:%S"),
        "date_created": raw_data["date_created"].strftime(time_format),
        "account_id": raw_data["account_id"],
        "event": raw_data["event"],
        "action": raw_data["action"],
        "product_id": raw_data["product_id"],
        "slug": raw_data["slug"],
        "result": raw_data["result"],
        "id" : _id
    }
    return prep_data

def index_grouping(normalized_data_list):
    d = dict()
    for i in normalized_data_list:
        if i['slug'] in list(d.keys()):
            d[i['slug']].append(i)
        else:
            d[i['slug']] = [i]
    return d

def get_duplicate(data_list):
    tmp = list()
    for index,i in enumerate(data_list):
        d = (i["account_id"],i["event"])
        tmp.append(d)
    count = 0
    result = dict()
    for index,i in enumerate(tmp):
        if tmp.count(i) > 1:
            if json.dumps(i) in result.keys():
                result[json.dumps(i)].append(index)
            else:
                result[json.dumps(i)] = [index]
    return result

def get_removed_elements(duplicate_elements):
    delete_elements = list()
    for indices in duplicate_elements.values():
        date_list = [datetime.datetime.strptime(normalized_data[i]['date'],"%Y-%m-%d %H:%M:%S") for i in indices]
        date_index = indices.pop(date_list.index(min(date_list)))
        delete_elements.extend(indices)
    return delete_elements

def sanitize_data(batch_data):
    normalized_data = [normalize(i) for i in sample_batch_0]
    duplicate_data = get_duplicate(batch_data)
    removed_index = get_removed_elements(duplicate_data)
    removed_items = [normalized_data[i] for i in removed_index]
    for i in removed_items:
        normalized_data.remove(i)
    return normalized_data

def get_active_user(datasets):
    simplified_data = [{"account_id": i['account_id'], "event": i['event']} for i in datasets]
    nonactive_user = list()
    for i in datasets:
        _tmp = {"account_id": i['account_id'], "event": "AccountTerminate"}
        if _tmp in simplified_data:
            nonactive_user.append(i['account_id'])
    nonactive_user = list(set(nonactive_user))
    active_user = [i for i in datasets if i['account_id'] not in nonactive_user ]
    return active_user