import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from utils import get_engine

load_dotenv()
# Load data
engine = get_engine()

df = pd.read_sql("SELECT * FROM jobs", engine)

df['created'] = pd.to_datetime(df['created'])
df['timestamp'] = pd.to_datetime(df['timestamp'])

col1, col2 = st.columns(2)

st.set_page_config(layout="wide", page_title="Job Dashboard", page_icon="📊")

import datetime

st.sidebar.markdown("### 📅 Filter by Date")

# Filter mode: Date Range or Single Date
filter_type = st.sidebar.radio("Filter type", ["Date Range", "Single Date"])

if filter_type == "Date Range":
    start_date, end_date = st.sidebar.date_input(
        "Select date range",
        [df['created'].min().date(), df['created'].max().date()]
    )
    date_mask = (df['created'].dt.date >= start_date) & (df['created'].dt.date <= end_date)
else:
    single_date = st.sidebar.date_input(
        "Select a date",
        df['created'].min().date()
    )
    date_mask = df['created'].dt.date == single_date

# Apply the filter to get filtered_df
filtered_df = df[date_mask]


with col1:
    st.subheader("📊 Top 20 Skills")
    # Explode skills for plotting
    skills_exp = filtered_df.copy()
    skills_exp['skills'] = skills_exp['skills'].fillna('').str.strip('{}')
    skills_exp = skills_exp.assign(skills=skills_exp['skills'].str.split(','))
    skills_exp = skills_exp.explode('skills')
    skills_exp['skills'] = skills_exp['skills'].str.strip().str.replace('"', '')

    top_skills = (
        skills_exp['skills']
        .value_counts()
        .head(20)
        .reset_index()
    )
    top_skills.columns = ['Skill', 'Count']

    fig_skills = px.bar(top_skills, x='Skill', y='Count', color='Count', title="Top 20 Skills")
    st.plotly_chart(fig_skills, use_container_width=True)

    st.subheader("📈 Jobs Over Time")

    if filter_type == "Date Range":
        job_counts = (
            filtered_df['created'].dt.date
            .value_counts()
            .sort_index()
            .reset_index()
        )
        job_counts.columns = ['Date', 'Job Count']
        fig = px.line(job_counts, x='Date', y='Job Count', markers=True)
        fig.update_layout(xaxis_title='Date', yaxis_title='Number of Jobs')

    else:  # Single Date → show by time (hour)
        job_counts = (
            filtered_df['created'].dt.hour
            .value_counts()
            .sort_index()
            .reset_index()
        )
        job_counts.columns = ['Hour', 'Job Count']
        job_counts['Hour'] = job_counts['Hour'].apply(lambda x: f"{x:02d}:00")
        fig = px.line(job_counts, x='Hour', y='Job Count', markers=True)
        fig.update_layout(xaxis_title='Time of Day', yaxis_title='Number of Jobs')

    st.plotly_chart(fig, use_container_width=True)


with col2:
    st.subheader("💰 Salary Distribution")

    # Filter out outliers using percentiles
    q_low = filtered_df['salary_max'].quantile(0.05)
    q_high = filtered_df['salary_max'].quantile(0.95)
    filtered_salaries = filtered_df[(filtered_df['salary_max'] >= q_low) & (filtered_df['salary_max'] <= q_high)]

    fig_salary = px.histogram(
        filtered_salaries,
        x='salary_max',
        nbins=10,
        title="Distribution of Max Salaries (5th–95th Percentile)",
        labels={'salary_max': 'Max Salary'},
        color_discrete_sequence=['teal']
    )

    st.plotly_chart(fig_salary, use_container_width=True)

    st.subheader("🏙️ Jobs by Location")

    jobs_by_location = (
        filtered_df['location']
        .value_counts()
        .head(15)
        .reset_index()
    )
    jobs_by_location.columns = ['Location', 'Job Count']

    fig_loc = px.bar(jobs_by_location, x='Location', y='Job Count', color='Job Count',
                    title="Top Locations by Job Count")
    st.plotly_chart(fig_loc, use_container_width=True)

# Show data
filtered_df['skills'] = filtered_df['skills'].fillna('').str.strip('{}').str.replace('"', '').str.strip('[]').str.replace("'",'').str.replace(',', ', ')
st.dataframe(filtered_df[['title', 'company', 'location', 'contract_type', 'salary_min', 'salary_max', 'skills']])
