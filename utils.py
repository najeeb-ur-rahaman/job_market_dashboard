import os
import pandas as pd
import json
from datetime import datetime
from sqlalchemy import create_engine

def save_raw_data(jobs, source="adzuna", directory = "datasets/raw"):
    os.makedirs(directory, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    filename = f"datasets/raw/{today}_{source}_jobs.json"
    with open(filename, 'w') as f:
        json.dump(jobs, f, indent=2)
    print(f"Saved raw data to {filename}")
    return filename

def load_raw_data(filename):
    with open(filename) as f:
        return json.load(f)
    
def save_processed_data(processed_jobs, source="adzuna", directory = "datasets/processed"):
    os.makedirs(directory, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    filename = f"datasets/processed/{today}_{source}_jobs.csv"
    df = pd.DataFrame(processed_jobs)
    df.to_csv(filename, index=False)
    print(f"Saved processed data to {filename}")
    return filename

def get_engine():
    return create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )