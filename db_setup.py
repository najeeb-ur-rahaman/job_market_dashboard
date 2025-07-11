import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_database():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname='postgres'
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Check if DB exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'job_market_db'")
        exists = cur.fetchone()

        if not exists:
            cur.execute("CREATE DATABASE job_market_db;")
            print("Database created.")
        else:
            print("Database already exists.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

def create_table():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname=os.getenv('DB_NAME')
        )
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id VARCHAR(50) PRIMARY KEY,
            title VARCHAR(255),
            company VARCHAR(255),
            contract_type VARCHAR(50),
            contract_time VARCHAR(50),
            created TIMESTAMP,
            location VARCHAR(255),
            category VARCHAR(100),
            salary_min FLOAT,
            salary_max FLOAT,
            description TEXT
        );
        """)
        conn.commit()
        print("Table ready.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

create_database()
create_table()