from app import db, psycopg2
import json

def get_columns(table):
    column = None
    try:
        # db.execute("SHOW columns FROM "+table)
        db.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name='"+table+"'")
        column = [row[0] for row in db.fetchall()]
    except (Exception, psycopg2.DatabaseError) as e:
        column = str(e)
    return column


def get_all(table):
    column = get_columns(table)
    results = list()
    try:
        db.execute("SELECT * FROM "+table)
        rows = db.fetchall()
        for row in rows:
            results.append(dict(zip(column, row)))
        return results
    except (Exception, psycopg2.DatabaseError) as e:
        return column + str(e)


def get_by_id(table, field= None, value= None):
    column = get_columns(table)
    results = list()
    try:
        query = "SELECT * FROM "+table+" WHERE "+field+"="+value
        db.execute("SELECT * FROM "+table+" WHERE "+field+"=%s",(value,))
        rows = db.fetchall()
        for row in rows:
            results.append(dict(zip(column, row)))
    except (Exception, psycopg2.DatabaseError) as e:
        raise e
    else:
        return results


def insert(table, data = None):
    value = ''
    column = ''
    for row in data:
        column += row+","
        value += "'"+str(data[row]+"',")
    column = "("+column[:-1]+")"
    value = "("+value[:-1]+")"
    try:
        db.execute("INSERT INTO "+table+" "+column+" VALUES "+value+" RETURNING *")
    except (Exception, psycopg2.DatabaseError) as e:
        raise e
    else:
        id_of_new_row = db.fetchone()[0]
        return str(id_of_new_row)

def update(table, tags, data = None):
    value = ''
    field = list()
    for key,value in data.items():
        field.append("{} = '{}'".format(key,value))
    field = ",".join(field)
    tags_key = list(tags.keys())
    tags_value = list(tags.values())
    status = None
    try:
        db.execute("UPDATE "+table+" SET "+field+" WHERE "+tags_key[0]+"="+tags_value[0]+"")
        status = True
    except (Exception, psycopg2.DatabaseError) as e:
        status = e
    finally:
        return status


def delete(table, field = None, value = None):
    rows_deleted = 0
    try:
        db.execute("DELETE FROM "+table+" WHERE "+field+" ="+value)
        rows_deleted = db.rowcount
    except (Exception, psycopg2.DatabaseError) as error:
        raise error
    else:
        return rows_deleted

