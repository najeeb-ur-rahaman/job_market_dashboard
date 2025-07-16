
import logging
import pandas as pd
from utils import save_raw_data, save_processed_data
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ------------------- Process Raw Jobs -------------------
def process_jobs(raw_jobs):
    processed = []
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    now = datetime.now().replace(second=0, microsecond=0)

    for job in raw_jobs:
        try:
            created_str = job.get("created", "")
            created_date = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%SZ").date()
            if created_date != yesterday:
                continue
        except (ValueError, TypeError):
            continue  # skip invalid or missing date

        salary_min = job.get('salary_min')
        salary_max = job.get('salary_max')

        if salary_min is None and salary_max is not None:
            salary_min = round(salary_max * 0.8, 2)
        elif salary_max is None and salary_min is not None:
            salary_max = round(salary_min * 1.2, 2)

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
            "timestamp": now
        })

    logger.info(f"Processed {len(processed)} jobs from raw data.")
    return processed

# ------------------- Main ETL Flow -------------------
def fetch_and_save_to_csv():
    logger.info("Fetching data from Adzuna API...")
    from api_client import fetch_jobs
    raw_jobs = fetch_jobs()

    from utils import save_raw_data, save_processed_data
    save_raw_data(raw_jobs)

    processed_jobs = process_jobs(raw_jobs)
    processed_file = save_processed_data(processed_jobs)

    logger.info("task1 completed successfully!")