import os
import psycopg2
from dotenv import load_dotenv


class DatabaseManager:
    def __init__(self, env_file=".env.prod"):
        load_dotenv(env_file)
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )

    def get_connection(self):
        return self.conn

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
