import psycopg2
import os
import logging
from psycopg2 import sql


logging.basicConfig(level=logging.INFO)


class db_manager:

    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host='localhost',
            port='5432'
        )

    def save_session(self, charging_session_data):
        # Create a cursor object
        cur = self.conn.cursor()

        # Insert statement
        insert_query = sql.SQL("""
            INSERT INTO charging_session (charging_station_id, user_id, start_time, stop_time, price, energy, tariff)
            VALUES (%s, %s, %s, %s, %s, %s , %s);
        """)
        try:
            # Execute the insertion
            cur.execute(insert_query, (
                charging_session_data['charging_station_id'],
                charging_session_data['user_id'],
                charging_session_data['start_time'],
                charging_session_data['stop_time'],
                charging_session_data['total_price'],
                charging_session_data['total_energy'],
                charging_session_data['tariff']
            ))

            # Commit the changes to the database
            self.conn.commit()
            print("Charging session inserted successfully")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()  # Rollback in case of error
        finally:
            # Close the cursor and connection
            cur.close()
            self.conn.close()

    def list_sessions(self):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT * FROM charging_session;
            """)
            rows = cur.fetchall()
            logging.info(rows)
            column_names = [desc[0] for desc in cur.description]
            result = [dict(zip(column_names, row)) for row in rows]
            logging.info("Fetched results", result)
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if cur:
                cur.close()
            if self.conn:
                self.conn.close()
