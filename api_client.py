import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

def fetch_jobs(pages=1):
    base_url = "http://api.adzuna.com/v1/api/jobs/gb/search/"
    all_jobs = []

    for page in range(1, pages + 1):
        url = f"{base_url}{page}"
        params = {
            "app_id": os.getenv("ADZUNA_APP_ID"),
            "app_key": os.getenv("ADZUNA_APP_KEY"),
            "what_or": "Data Engineer Data Scientist Data Analyst, Machine Learning Engineer Business Intelligence Data Architect Database Administrator ETL Developer Analytics Engineer",
            "max_days_old": 1,
            "results_per_page": 2
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data:
                all_jobs.extend(data['results'])
                print(f"Fetched page {page} with {len(data['results'])} jobs.")
            else:
                print(f"No results on page {page}.")
        
        except requests.exceptions.RequestException as req_err:
            print(f"Request error on page {page}: {req_err}")
        except ValueError as val_err:
            print(f"JSON decode error on page {page}: {val_err}")
        except Exception as e:
            print(f"Unexpected error on page {page}: {e}")
        
        time.sleep(0.100)  # optional: avoid hitting rate limits

    print(f"Total jobs fetched: {len(all_jobs)}")
    return all_jobs