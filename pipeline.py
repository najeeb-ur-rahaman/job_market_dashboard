import logging
from utils import get_engine
from datetime import datetime, timedelta
from db_setup import create_table
from sqlalchemy import Table, MetaData
from sqlalchemy.dialects.postgresql import insert
from skill_extractor import SkillExtractor

extractor = SkillExtractor()

# ------------------- Set up logging -------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
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
            salary_min = salary_max * 0.8
        elif salary_max is None and salary_min is not None:
            salary_max = salary_min * 1.2

        logger.info(f"Extracting skills for job ID: {job.get('id', '')}")
        skills = extractor.extract(job.get("description", ""))

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
            "skills": skills,
            "description": job.get("description", ""),
            "timestamp": now
        })

    logger.info(f"Processed {len(processed)} jobs from raw data.")
    return processed

# ------------------- Save Processed Jobs to DB -------------------
def save_to_db(processed_jobs):
    if not processed_jobs:
        logger.warning("No processed jobs to save.")
        return

    try:
        engine = get_engine()
        metadata = MetaData()
        metadata.reflect(bind=engine)
        jobs_table = metadata.tables.get('jobs')

        if jobs_table is None:
            raise Exception("Table 'jobs' not found in the database.")

        # Remove duplicates based on job_id
        unique_jobs = {job["job_id"]: job for job in processed_jobs}
        logger.info(f"Saving {len(unique_jobs)} unique jobs to the database...")

        with engine.begin() as conn:
            stmt = insert(jobs_table).values(list(unique_jobs.values()))
            stmt = stmt.on_conflict_do_nothing(index_elements=['job_id'])  # Deduplication
            conn.execute(stmt)

        logger.info(f"Inserted {len(unique_jobs)} job(s) into the database.")
    except Exception as e:
        logger.exception("Failed to save processed jobs to the database.")
        raise

# ------------------- Main ETL Flow -------------------
def main():
    logger.info("Fetching data from Adzuna API...")
    from api_client import fetch_jobs
    raw_jobs = fetch_jobs()

    from utils import save_raw_data, save_processed_data
    raw_file = save_raw_data(raw_jobs)

    processed_jobs = process_jobs(raw_jobs)
    processed_file = save_processed_data(processed_jobs)

    create_table()  # Ensures DB/table exists
    save_to_db(processed_jobs)

    logger.info("Pipeline completed successfully!")