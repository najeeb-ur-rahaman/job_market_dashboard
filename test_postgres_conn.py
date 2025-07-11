import os
from dotenv import load_dotenv

load_dotenv()

def create_database_if_not_exists():
    import psycopg2
    from psycopg2 import sql

    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname=os.getenv('DB_NAME')
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Check if DB exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'jobs_db'")
        exists = cur.fetchone()

        if not exists:
            cur.execute("CREATE DATABASE jobs_db;")
            print("Database created.")
        else:
            print("Database already exists.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

create_database_if_not_exists()