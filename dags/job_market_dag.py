from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, '/opt/airflow/project')

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email': ['snajeebr07@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False
}

def run_pipeline():
    from pipeline import main
    main()

with DAG(
    'job_market_pipeline',
    default_args=default_args,
    description='Daily job market data pipeline',
    schedule_interval='0 10 * * *',
    start_date=datetime(2025,7,15),
    catchup=False
) as dag:

    run_task = PythonOperator(
        task_id = 'run_pipeline',
        python_callable=run_pipeline,
        execution_timeout=timedelta(minutes=15)
    )