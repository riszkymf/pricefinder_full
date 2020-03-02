import json
import datetime
import calendar

from app import logging
from dateutil.relativedelta import relativedelta


es_filter_date = {
    "days": "d",
    "months": "M",
    "years": "y"
}


date_format = {
    "full": "%Y-%m-%d",
    "month": "%Y-%m",
    "year": "%Y"
}


def date_normalize(date_str):
    if date_str == None:
        return None
    elif date_str.lower() == "now":
        return "now"
    check = False
    param_key = None
    for key,val in date_format.items():
        try:
            date = datetime.datetime.strptime(date_str,val)
        except ValueError:
            pass
        else:
            param_key = key
            check = check or True
            break
    if check:
        if param_key == 'month':
            month_range = calendar.monthrange(date.year,date.month)
            str_date = "{}-{}-01".format(date.strftime("%Y"),date.strftime("%m"))
            return str_date
        elif param_key == 'full':
            tmp = date_str.split("-")
            if len(tmp[-1]) != 2:
                tmp[-1] = "0" + str(tmp[-1])
                return "-".join(tmp)
            else:
                return date_str
            return date_str
        elif param_key == 'year':
            str_date = "{}-01-01".format(date.strftime("%Y"))
            return str_date
    else:
        year_ago = datetime.datetime.now() - relativedelta(years=1)
        date = "{}-01-01".format(year_ago.year)
        return date

def range_date(date_field, date_from=None, date_to=None, date_filter=None, _round=False):
    """
    date_from must be less than or equals date_to. It must follow one of the following format :
     - YYYY-MM-DD
     - YYYY-MM
     - YYYY
     - now

    date_filter is used to unspecified date. Example: 
        {
            months: 6
        }
        will filter results 6 months back from current date.
    """
    if date_filter != None:
        q_round = ''
        key,value = list(date_filter.items())[0]
        tag = es_filter_date.get(key,"M")
        if _round:
            q_round = "/" + tag
        es_filter = "now-{}{}".format(value,tag) + q_round
        date_to = "now"
        date_from = es_filter
    else:
        date_from = date_normalize(date_from)
        date_to = date_normalize(date_to)
    range_query = {
            "range": {
                date_field :
                    {
                        "gte": date_from,
                        "lte": date_to
                    }
                }
            }   
    return range_query

def match_query(field_filter):
    queries = list()
    for key,value in field_filter.items():
        query = {"match":{}}
        query['match'][key] = {"query": value}
        queries.append(query)
    return queries

def build_queries(queries):
    query = {
        "query":{
            "bool": {
                "must": queries
            }
        }
    }
    return query


def date_filter(_filter, date_field="date_created"):
    if 'date_filter' in list(_filter.keys()):
        _round = False
        try:
            _round = _filter["date_filter"].get("round",False)
            _round = bool(_round)
        except Exception as e:
            logging.error(str(e))
            pass
        query = range_date(date_filter=_filter['date_filter'], date_field=date_field, _round=_round)
        return query
    else:
        _from = _filter.get('from',None)
        _to = _filter.get('to',None)
        query = range_date(date_from=_from,date_to=_to, date_field=date_field)
        return query