import os
import time

import pymysql

db_host = os.getenv("DB_HOST", "db")
db_port = int(os.getenv("DB_PORT", 3306))
db_user = os.getenv("DB_USER", "tembi_user")
db_pass = os.getenv("DB_PASS", "tembi_pass")
db_name = os.getenv("DB_NAME", "tembi")

while True:
    try:
        conn = pymysql.connect(
            host=db_host, port=db_port, user=db_user, password=db_pass, database=db_name
        )
        conn.close()
        print("Database is ready!")
        break
    except Exception:
        print("Waiting for database...")
        time.sleep(2)
