# 💼 UK Job Market Analysis (Cloud Version)

An end-to-end data pipeline that collects, processes, stores, and visualizes UK tech job data using the [Adzuna API](https://developer.adzuna.com/). Built with **Apache Airflow**, **Python**, **Neon (PostgreSQL)**, and **Streamlit**.

## 🧩 Features

- 🔄 Daily job data ingestion via Adzuna API
- 🧠 Automatic skill extraction using `facebook/bart-large-mnli` model
- 🗃️ Data stored in Neon PostgreSQL (cloud database)
- 📊 Interactive dashboard with filters and insights using Streamlit
- 📅 Backfill-safe design (fetches yesterday’s data)

## 📷 Preview

![Dashboard Screenshot](assets/dashboard-overview.jpg)

## 🔧 Architecture Overview

![Architechture Screenshot](assets/architechture.png)

## 🗂️ Project Structure

```
job\_market\_dashboard/
│
├── dags/                      # Airflow DAG scripts
│   └── job\_market\_dag.py
│
├── datasets/                  # Local storage
│   ├── raw/                   # Raw JSON data
│   └── processed/             # Transformed CSV files
│
├── api_client.py
├── dashboard.py
├── jobs_table.py
├── skill_extractor.py
├── skills.py
├── task1.py
├── task2.py
├── utils.py
│
├── docker-compose.yml         # Multi-service Docker setup
├── .env.example               # Sample environment config
└── README.md
```

## 🔐 Environment Variables

Create a `.env` file in your project root:

```env
# Adzuna API
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_api_key

# Neon PostgreSQL Connection String
NEON_URL=postgresql://username:password@your-project.neon.tech/dbname
```

> 🔒 **Never commit your `.env` file to GitHub.**

## ⚙️ Airflow DAG Details

- **Frequency**: Daily
- **Logic**: Pulls **yesterday’s** jobs to ensure complete data
- **Tasks**:

  - `fetch_and_save_to_csv`: Pulls from API, transforms JSON to CSV
  - `load_csv_to_db`: Extracts skills using BART model & uploads to Neon DB

> ✅ The jobs table is stored in `job_market.job_market_db.dev.jobs`

## 🧾 Neon PostgreSQL Table Schema

```sql
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
```

## 📊 Dashboard Filters

- Filter by **single date** or **date range**
- Visual insights:

  - 🔝 Top 20 Skills
  - 💰 Salary Distribution
  - 📍 Top Locations
  - 📈 Jobs Over Time

## ▶️ Running Locally

> Requires Docker and Docker Compose installed.

```bash
docker-compose up --build
```

- Access Airflow UI: [http://localhost:8080](http://localhost:8080)
- Access Streamlit Dashboard: [http://localhost:8501](http://localhost:8501)

## 🛠️ Tech Stack

- **Airflow** for orchestration
- **Python** (pandas, requests, transformers)
- **HuggingFace Transformers** for skill extraction
- **Neon PostgreSQL** for cloud DB
- **Streamlit** for dashboarding
- **Docker** for containerization

## 🧑‍💻 Author

**Najeeb ur Rahaman**
[GitHub](https://github.com/najeeb-ur-rahaman) | [LinkedIn](https://www.linkedin.com/in/snajeebr)
