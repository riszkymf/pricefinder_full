import os

from cron_tasks.tasks import VPN_ES


ES_HOST = os.getenv("ES_HOST","http://103.89.5.160:9200")

ES_USERNAME = os.getenv("ES_USERNAME","elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD","BiznetGio2017")

es_vpn = VPN_ES(ES_HOST,ES_USERNAME,ES_PASSWORD)


es_vpn.test_connection()
es_vpn.pull_configs()