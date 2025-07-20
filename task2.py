import os
import logging
import pandas as pd
from datetime import datetime
from jobs_table import create_table
from sqlalchemy import create_engine, inspect
from skill_extractor import SkillExtractor
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine, Table, MetaData
from utils import get_engine

logger = logging.getLogger(__name__)
def extract_skills_from_csv(df):
    logger.info(f"Loaded {len(df)} records")

    logger.info("Initializing the extractor...")
    extractor = SkillExtractor()

    def extract_skills(description):
        logger.info("Extracting skills...")
        try:
            return extractor.extract(description)
        except Exception as e:
            return []

    df['skills'] = df['description'].apply(extract_skills)
    logger.info("Extraction finished")
    return df

# ------------------- Save Processed Jobs to DB -------------------
def save_to_db(df):
    try:
        logger.info("removing the duplicated within the dataframe")
        df.drop_duplicates(subset="job_id", inplace=True)
        logger.info("Creating engine...")
        engine = get_engine()

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
def load_csv_to_db():
    
    today_str = datetime.today().strftime("%Y%m%d")
    processed_file = f"{today_str}_adzuna_jobs.csv"
    filepath = os.path.join("datasets", "processed", processed_file)

    # Read the CSV file
    print(f" Reading the CSV file {filepath}")
    if os.path.exists(filepath):
        skills_df = extract_skills_from_csv(pd.read_csv(filepath))

        create_table()  # Ensures DB/table exists
        save_to_db(skills_df)

        logger.info("task2 completed successfully!")
    else:
        raise FileNotFoundError(f"No CSV file found for today at: {filepath}")
