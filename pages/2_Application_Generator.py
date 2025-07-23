import streamlit as st
import openai
from openai import OpenAI
import urllib.parse

from modules.fetch_news import fetch_company_news
from modules.parse_job_ad import extract_job_objectives
from modules.profile_utils import (
    load_user_profile,
    increment_usage,
    save_application_to_history,
    can_generate_application
)
from modules.payment import create_checkout_session
from modules.ui_sections import render_job_inputs, render_news_section, render_optional_inputs, render_profile_view

# Set up OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Application Generator", page_icon="📄")
st.title("📄 Job Application Generator")


def normalize_company_name(name):
    aliases = {
        "JP Morgan": "JPMorgan Chase",
        "J.P. Morgan": "JPMorgan Chase",
        "Google": "Alphabet Inc",
        "Meta": "Meta Platforms",
        "Facebook": "Meta Platforms",
    }
    return aliases.get(name.strip(), name.strip())


@st.cache_data(ttl=3600)
def fetch_company_news_cached(company_name):
    return fetch_company_news(company_name)


# --- Email + usage logic ---
email = st.text_input("Enter your email to load config", key="email_jobgen")
query_params = st.query_params
payment_complete = query_params.get("paid", ["0"])[0] == "1"

if email:
    profile = load_user_profile(email)

    st.markdown("### 💰 Usage & Upgrade Options")
    st.markdown("""
    - ✅ **Free Tier** — 2 job applications/week  
    - 🪙 **Pay-per-use** — [$3 AUD per app](https://buy.stripe.com/test_cNi8wP3CN7ni6pMczkjd00)  
    - 🏆 **Pro Subscription** — *$10/month — coming soon*

    After payment, refresh the page or re-enter your email to continue.
    """)

    if not can_generate_application(profile):
        st.error("❌ You've reached your weekly limit.")
        if st.button("🔓 Unlock 1 more application ($3 AUD)"):
            url = create_checkout_session(email)
            st.markdown(f"[Click here to pay →]({url})")
            st.stop()
        st.info("After payment, this page will reload automatically. If not, refresh or re-enter your email.")
        st.stop()

    # ✅ Apply session defaults via dictionary
    defaults = {
        "job_title": "",
        "company": "",
        "job_ad_text": "",
        "recent_news": "",
        "strategy_docs": "",
        "job_objectives": ""
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    # --- Modular UI blocks ---
    render_job_inputs()
    render_news_section(normalize_company_name, fetch_company_news_cached)
    render_optional_inputs()
    render_profile_view(profile)
