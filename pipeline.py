import os
from utils import *
from datetime import datetime, timedelta
from db_setup import create_table
from sqlalchemy import create_engine

def process_jobs(raw_jobs):
    processed = []
    yesterday = datetime.utcnow().date() -  timedelta(days=1)

    for job in raw_jobs:
        # Parse created date
        created_str = job.get("created", "")
        try:
            created_date = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ").date()
        except (ValueError, TypeError):
            continue  # Skip if invalid or missing date

        if created_date != yesterday:
            continue  # Skip if not today's job
        
        # Handle salary estimation
        salary_min = job.get('salary_min')
        salary_max = job.get('salary_max')

        if salary_min is None and salary_max is not None:
            salary_min = salary_max * 0.8  # Estimate 20% below max
        elif salary_max is None and salary_min is not None:
            salary_max = salary_min * 1.2  # Estimate 20% above min

        processed.append({
            "job_id": job.get("id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", {}).get("display_name", ""),
            "contract_type": job.get("contract_type", "unknown"),
            "contract_time": job.get("contract_time", "unknown"),
            "created": created_str,
            "location": job.get("location", {}).get("display_name", ""),
            "category": job.get("category", {}).get("label", ""),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "description": job.get("description", ""),
            "timestamp": pd.to_datetime('today').strftime('%d-%m-%Y %H:%M')
        })
    return processed

def save_to_db(processed_jobs):
    # Create DataFrame
    df = pd.DataFrame(processed_jobs)
    
    try:
        # Create database connection
        engine = create_engine(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        
        # Save to database
        df.to_sql('jobs', engine, if_exists='append', index=False)
        print(f"Inserted {len(df)} records to jobs table")
    except Exception as e:
        print(f"Error: {e}")

def main():
    # Fetch jobs from api_client.py
    print('Fetching data from Adzuna API...')
    from api_client import fetch_jobs
    raw_jobs = fetch_jobs()
    
    # Save raw data
    raw_file = save_raw_data(raw_jobs)
    
    # Process data
    processed_jobs = process_jobs(raw_jobs)
    
    # Save processed data
    processed_file = save_processed_data(processed_jobs)
    
    # call the create database and table function in the db_setup file
    create_table()
    
    # load the data into the table using pandas
    save_to_db(processed_jobs)
    
    print("Pipeline completed successfully!")