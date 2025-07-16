import os
import logging
import pandas as pd
from utils import save_raw_data, save_processed_data
from datetime import datetime, timedelta
from db_setup import create_table
from sqlalchemy import create_engine, inspect
from skill_extractor import SkillExtractor
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine, Table, MetaData

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

def extract_skills_from_csv(csv_file_path):
    logger.info("reading the CSV file")
    df = pd.read_csv(csv_file_path)

    extractor = SkillExtractor()

    def extract_skills(description):
        logger.info("Extracting skills...")
        try:
            return extractor.extract(description)
        except Exception as e:
            return []

    df['skills'] = df['description'].apply(extract_skills)
    return df

# ------------------- Save Processed Jobs to DB -------------------
def save_to_db(df):
    try:
        df.drop_duplicates(subset="job_id", inplace=True)
        logger.info("Creating engine...")
        engine = create_engine(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

        logger.info("Preparing insert with ON CONFLICT DO NOTHING...")
        metadata = MetaData()
        jobs_table = Table("jobs", metadata, autoload_with=engine)

        stmt = insert(jobs_table).values(df.to_dict(orient='records'))
        stmt = stmt.on_conflict_do_nothing(index_elements=["job_id"])  # assumes job_id is unique or primary key

        with engine.begin() as conn:
            result = conn.execute(stmt)

        logger.info(f"Inserted {result.rowcount} new records into the database.")
    except Exception as e:
        logger.error(f"Failed to save to database: {e}")
        raise

# ------------------- Main ETL Flow -------------------
def main():
    logger.info("Fetching data from Adzuna API...")
    from api_client import fetch_jobs
    raw_jobs = fetch_jobs()

    from utils import save_raw_data, save_processed_data
    save_raw_data(raw_jobs)

    processed_jobs = process_jobs(raw_jobs)
    processed_file = save_processed_data(processed_jobs)

    print(" Reading the CSV file...")
    skills_df = extract_skills_from_csv(processed_file)

    create_table()  # Ensures DB/table exists
    save_to_db(skills_df)

    logger.info("Pipeline completed successfully!")