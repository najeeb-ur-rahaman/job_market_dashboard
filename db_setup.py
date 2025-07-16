import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
def jobs_table():
    try:
        print(f"Connecting to Database {os.getenv('DB_NAME')} ...")
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            dbname=os.getenv('DB_NAME')
        )
        cur = conn.cursor()

        print('Creating table jobs..')

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
            skills TEXT,
            description TEXT,
            timestamp TIMESTAMP
        );
        """)
        conn.commit()
        print("Table ready.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

def create_table():
    jobs_table()