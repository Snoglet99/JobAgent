import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Operator Agent - Job Application", layout="centered")

st.title("🧠 Operator Agent: Tailored Job Application Generator")

with st.form("job_form"):
    st.header("🔍 Job Details")

    job_title = st.text_input("Job Title*", placeholder="e.g. Head of Strategy", max_chars=100)
    company = st.text_input("Company Name*", placeholder="e.g. Cru Tech", max_chars=100)
    location = st.text_input("Location", placeholder="e.g. Sydney, Remote", max_chars=100)
    industry = st.selectbox("Industry (optional)", ["", "Tech", "Finance", "Energy", "Healthcare", "Education", "Other"])
    stage = st.selectbox("Company Stage (optional)", ["", "Startup", "Scale-up", "Corporate", "Government", "Other"])

    st.markdown("---")
    st.header("📋 Job Ad Content")

    job_ad_text = st.text_area("Paste the full job ad*", height=300)

    st.markdown("---")
    st.header("🎯 Context & Customisation")

    tone_profile = st.selectbox(
        "Choose a tone/profile",
        ["Default", "Visionary", "Fixer", "Leader", "Team Player", "Entrepreneur"]
    )

    context_link_1 = st.text_input("Optional Context Link 1 (e.g. annual report)")
    context_link_2 = st.text_input("Optional Context Link 2 (e.g. media release)")
    context_link_3 = st.text_input("Optional Context Link 3 (e.g. company initiative)")

    include_resume_bullets = st.checkbox("Include Resume Bullets in Output", value=True)

    submitted = st.form_submit_button("🚀 Generate Application")

if submitted:
    # Placeholder logic – replace with GPT + output module
    st.success("Generating your application...")

    # Collect inputs into a dict to pass downstream
    application_data = {
        "job_title": job_title,
        "company": company,
        "location": location,
        "industry": industry,
        "stage": stage,
        "job_ad": job_ad_text,
        "tone": tone_profile,
        "context_links": [context_link_1, context_link_2, context_link_3],
        "include_resume_bullets": include_resume_bullets,
        "timestamp": datetime.utcnow().isoformat()
    }

    st.json(application_data)  # for dev debugging – remove in production
