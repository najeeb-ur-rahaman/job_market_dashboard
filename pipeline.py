from utils import *

def process_jobs(raw_jobs):
    processed = []
    for job in raw_jobs:
        # Get full description if truncated
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
            "created": job.get("created", ""),
            "location": job.get("location", {}).get("display_name", ""),
            "category": job.get("category", {}).get("label", ""),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "description": job.get("description", "")
        })
    return processed

if __name__ == "__main__":
    # Fetch jobs from api_client.py
    from api_client import fetch_jobs
    raw_jobs = fetch_jobs()
    
    # Save raw data
    raw_file = save_raw_data(raw_jobs)
    
    # Process data
    processed_jobs = process_jobs(raw_jobs)
    
    # Save processed data
    processed_file = save_processed_data(processed_jobs)
    
    print("Pipeline completed successfully!")