import os
from dotenv import load_dotenv
from utils import get_engine
load_dotenv()

from sqlalchemy import Table, Column, String, MetaData, Text, DateTime, Float

def jobs_table():

    print('Creating table jobs..')
    metadata = MetaData(schema="dev")

    jobs = Table(
        "jobs", metadata,
        Column("job_id", String(50), primary_key=True),
        Column("title", String(255)),
        Column("company", String(255)),
        Column("contract_type", String(50)),
        Column("contract_time", String(50)),
        Column("created", DateTime),
        Column("location", String(255)),
        Column("category", String(100)),
        Column("salary_min", Float),
        Column("salary_max", Float),
        Column("skills", Text),
        Column("description", Text),
        Column("timestamp", DateTime),
    )

    metadata.create_all(get_engine())