from utils import save_raw_data, save_processed_data

def process_jobs(raw_jobs):
    processed = []
    for job in raw_jobs:
        processed.append({
            "job_id": job.get("id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", {}).get("display_name", ""),
            "contract_type": job.get("contract_type", ""),
            "contract_time": job.get("contract_time", ""),
            "created": job.get("created", ""),
            "location": job.get("location", {}).get("display_name", ""),
            "category": job.get("category", {}).get("label", ""),
            "salary_min": job.get("salary_min", ""),
            "salary_max": job.get("salary_max", ""),
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