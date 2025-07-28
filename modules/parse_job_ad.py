import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_job_objectives(job_title: str, job_ad_text: str) -> dict:
    prompt = f"""
You are a senior job analyst AI. Parse the following job title and job ad to extract structured objectives.

Return your output as JSON with the following fields:
- core_objectives: list of clear goals the role is meant to achieve
- key_focus_areas: main responsibilities or capability domains
- pain_points: inferred challenges the company or role is trying to solve
- target_metrics: any implied or explicit targets (financial, team, operational)

JOB TITLE: {job_title}

JOB AD TEXT:
{job_ad_text}

Return only the JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a structured information extractor for job postings."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
