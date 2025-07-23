import streamlit as st
import openai
from openai import OpenAI
import urllib.parse

from modules.fetch_news import fetch_company_news
from modules.parse_job_ad import extract_job_objectives
from modules.profile_utils import (
    load_user_profile,
    save_user_profile,
    save_application_to_history,
)
from modules.payment import create_checkout_session
from modules.ui_sections import render_job_inputs, render_news_section, render_optional_inputs, render_profile_view
from modules.generate_cover_letter import generate_cover_letter  # ✅ Added

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


# --- Access Logic ---
def has_application_access(profile):
    return profile.get("usage_count", 0) < 3 or profile.get("paid_access", False)


def increment_usage_or_block(profile, email):
    if profile.get("usage_count", 0) < 3:
        profile["usage_count"] = profile.get("usage_count", 0) + 1
        profile["edit_rounds"] = 0
        save_user_profile(email, profile)
        return True
    return False


# --- Email + usage logic ---
email = st.text_input("Enter your email to load config", key="email_jobgen")
query_params = st.query_params

if email:
    profile = load_user_profile(email)

    # Handle Stripe redirect
    if query_params.get("paid") and query_params.get("paid")[0] == "1":
        profile["paid_access"] = True
        profile["edit_rounds"] = 0
        save_user_profile(email, profile)
        st.experimental_set_query_params(email=email)
        st.success("✅ Payment successful. You can now generate and edit your next application.")

    # Lock if user has no access
    if not has_application_access(profile):
        st.error("❌ You've used all 3 free applications.")
        st.markdown("### 💰 Usage & Upgrade Options")
        st.markdown("""
        ✅ **Free Tier** — 3 total applications per email  
        🔁 **Each includes 3 cover letter refinements**  
        🪙 **Pay-per-use** — $3 AUD per application  
        🏆 **Pro Subscription** — $10/month *(coming soon)*  
        """)
        url = create_checkout_session(email)
        st.markdown("After payment, this page will reload automatically.")
        st.markdown(f"[🔓 Unlock 1 more application for $3 AUD →]({url})", unsafe_allow_html=True)
        st.stop()

    # --- UI session defaults ---
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

    # --- Generate ---
    if st.button("📝 Generate Cover Letter"):
        if profile.get("edit_rounds", 0) == 0:
            if not increment_usage_or_block(profile, email):
                st.warning("No more free applications. Please purchase another.")
                st.stop()

        # ✅ Extract job objectives if not already
        if not st.session_state["job_objectives"]:
            st.session_state["job_objectives"] = extract_job_objectives(st.session_state["job_ad_text"])

        # ✅ Generate cover letter
        st.session_state["generated_text"] = generate_cover_letter(
            job_title=st.session_state["job_title"],
            company=st.session_state["company"],
            job_ad_text=st.session_state["job_ad_text"],
            job_objectives=st.session_state["job_objectives"],
            profile=profile,
            news=st.session_state["recent_news"],
            strategy=st.session_state["strategy_docs"],
            tone=profile.get("tone", "Default")
        )
        st.success("✅ Cover letter generated!")

    # --- Show Output + Improve ---
    if "generated_text" in st.session_state:
        st.markdown("### ✉️ Your Cover Letter")
        st.text_area("Output", value=st.session_state["generated_text"], height=300, key="output", disabled=False)

        if "edit_rounds" not in profile:
            profile["edit_rounds"] = 0

        if st.button("🔁 Improve Cover Letter"):
            if profile["edit_rounds"] < 3:
                profile["edit_rounds"] += 1
                save_user_profile(email, profile)
                st.experimental_rerun()
            else:
                profile["paid_access"] = False
                save_user_profile(email, profile)
                st.warning("⚠️ You've reached your 3 refinements. Please purchase another application to continue.")
