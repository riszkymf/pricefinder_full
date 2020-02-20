from sshtunnel import SSHTunnelForwarder
from app import logging

import sshtunnel
import os

TUNNEL_HOST = os.environ.get("TUNNEL_HOST", os.getenv('TUNNEL_HOST'))
TUNNEL_PORT = os.environ.get("TUNNEL_PORT", os.getenv('TUNNEL_PORT'))
REMOTE_BIND_ADDRESS = os.environ.get("REMOTE_BIND_ADDRESS", os.getenv('REMOTE_BIND_ADDRESS'))
REMOTE_BIND_PORT = os.environ.get("REMOTE_BIND_PORT", os.getenv('REMOTE_BIND_PORT'))
TUNNEL_USERNAME = os.environ.get("TUNNEL_USERNAME", os.getenv('TUNNEL_USERNAME'))
TUNNEL_PASSWORD = os.environ.get("TUNNEL_PASSWORD", os.getenv('DB_NTUNNEL_PASSWORDAME'))

def query_log():
    q = """
SELECT *
FROM hb_account_logs hal
LEFT JOIN hb_accounts ha ON hal.account_id = ha.id
LEFT JOIN hb_products hp ON ha.product_id = hp.id
LEFT JOIN hb_categories hc ON hp.category_id = hc.id
WHERE hc.id = '78' and hal.result='1'
GROUP BY account_id
HAVING COUNT(account_id) > 1"""
    return q

def db_query_tunnel(db, query):
    try:
        with sshtunnel.open_tunnel(
            ssh_address_or_host=(TUNNEL_HOST, TUNNEL_PORT),
            remote_bind_address=(REMOTE_BIND_ADDRESS, REMOTE_BIND_PORT),
            ssh_username=TUNNEL_USERNAME,
            ssh_password=TUNNEL_PASSWORD,
            block_on_close=False
        ) as tunnel:
            logging.info('Connection to tunnel ({}:{}) OK...'.format(tunnel_host,tunnel_port))
            conn = db
            conn.MYSQL_DATABASE_PORT = tunnel.local_bind_port
            conn.start_connection()
            with conn.connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
    except Exception as e:
        logging.error(str(e))
    return data

def db_query(db,query):
    try:
        conn = db
        conn.MYSQL_DATABASE_PORT = tunnel.local_bind_port
        conn.start_connection()
        with conn.connection.cursor() as cursor:
            cursor.execute(q_create)
            data = cursor.fetchall()
    except Exception :
        logging.error(str(e))
        return list()
    else:
        return data