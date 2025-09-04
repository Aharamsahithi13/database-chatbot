import pymysql
from typing import List, Dict, Union
from configure import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def get_mysql_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        autocommit=True
    )

def execute_sql(sql: str) -> List[Dict[str, Union[int, str]]]:
    conn = get_mysql_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def test_connection():
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            return cursor.fetchall()
    except Exception as e:
        return str(e)
    finally:
        if 'conn' in locals():
            conn.close()
