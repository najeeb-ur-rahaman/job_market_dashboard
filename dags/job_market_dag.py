from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, '/opt/airflow/project')

default_args = {
    'owner': 'airflow',
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

def API_to_CSV():
    from task1 import fetch_and_save_to_csv
    fetch_and_save_to_csv()

def CSV_to_DB():
    from task2 import load_csv_to_db
    load_csv_to_db()

with DAG(
    'job_market_pipeline',
    default_args=default_args,
    description='Daily job market data pipeline',
    schedule_interval='0 20 * * *',
    start_date=datetime(2025,7,15),
    catchup=False
) as dag:

    API_to_CSV_task = PythonOperator(
        task_id = 'fetch_and_save_to_csv',
        python_callable=API_to_CSV,
        execution_timeout=timedelta(minutes=5)
    )

    CSV_to_DB_task = PythonOperator(
    task_id = 'load_csv_to_db',
    python_callable=CSV_to_DB,
    execution_timeout=timedelta(minutes=15)
    )

    API_to_CSV_task >> CSV_to_DB_task