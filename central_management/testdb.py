import psycopg2
import json
import os
from flask import Flask, send_from_directory, request, jsonify, make_response

app = Flask(__name__)
print(os.environ)
conn = psycopg2.connect(
            dbname='ev_db',
            user='ev_user',
            password='ev_pass',
            host='192.168.0.12',
            port='5432'
        )
try:
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM charging_session;
    """)
    rows = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]
    print(column_names)
    result = [dict(zip(column_names, row)) for row in rows]
    print(result)
    with app.app_context():
        json_result = jsonify(result)

    print(json_result)
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()