import streamlit as st
from modules.parse_job_ad import extract_job_objectives
import urllib.parse


def render_job_inputs():
    st.markdown("### 📄 Job Details")
    st.session_state.job_title = st.text_input("Job Title", value=st.session_state.job_title)
    company_input = st.text_input("Company Name", value=st.session_state.get("company", ""))
    st.session_state.company = company_input
    st.session_state.job_ad_text = st.text_area("Paste Job Ad Text or Summary", height=200, value=st.session_state.job_ad_text)

    if st.button("🧠 Extract Job Objectives"):
        if not st.session_state.job_ad_text.strip():
            st.warning("Paste the full job description or summary — not just the job title.")
        else:
            parsed = extract_job_objectives(st.session_state.job_title, st.session_state.job_ad_text)
            st.session_state.job_objectives = parsed

    if "job_objectives" in st.session_state and st.session_state.job_objectives:
        st.markdown("### ✅ Parsed Job Objectives")
        st.json(st.session_state.job_objectives)


def render_news_section(normalize_company_name, fetch_company_news_cached):
    if st.button("📰 Fetch Company News"):
        company_name = normalize_company_name(st.session_state.get("company", "").strip())
        st.caption("Use exact legal name (e.g. 'JPMorgan Chase').")
        if not company_name:
            st.error("❌ Company name required.")
        else:
            try:
                news = fetch_company_news_cached(company_name)
                if "No relevant articles" in news or "Error" in news:
                    st.error(news)
                else:
                    st.session_state.auto_news_summary = news
                    st.subheader("📌 Fetched News")
                    st.markdown(news.replace('\n', '  \n'))
            except Exception as e:
                st.error(f"❌ News fetch failed: {e}")

    if st.session_state.job_title and st.session_state.company:
        news_link = generate_news_url(st.session_state.company, st.session_state.job_title)
        st.markdown("### 🔍 Manual News Search")
        st.markdown(f"[Google News →]({news_link})", unsafe_allow_html=True)


def generate_news_url(company, job_title):
    company_clean = company.replace("Pty Ltd", "").replace("Ltd", "").strip('" ')
    company_encoded = urllib.parse.quote_plus(f'"{company_clean}"')
    job_keywords = job_title.lower()

    if any(kw in job_keywords for kw in ["sales", "revenue", "account", "business development"]):
        keywords = ["revenue", "market expansion", "client acquisition"]
    elif any(kw in job_keywords for kw in ["ceo", "executive", "strategy", "director"]):
        keywords = ["leadership change", "acquisition", "corporate strategy"]
    else:
        keywords = ["hiring", "product launch", "company update"]

    query = f'{company_encoded} AND ' + " OR ".join([f'"{kw}"' for kw in keywords])
    return f"https://www.google.com/search?q={query}&tbm=nws"


def render_optional_inputs():
    st.markdown("### 🧠 Optional Context")
    st.session_state.recent_news = st.text_area("Paste relevant media releases/news", value=st.session_state.recent_news)
    st.session_state.strategy_docs = st.text_area("Paste annual reports/strategy docs", value=st.session_state.strategy_docs)


def render_profile_view(profile):
    st.markdown("### 👤 Profile Snapshot (not editable here)")
    tone = profile.get("tone", "Default")
    summary = profile.get("cv_summary", "")
    bullets = profile.get("resume_bullets", "")
    variant = profile.get("profile_variant", "Leader")

    st.text(f"Tone: {tone}")
    st.text(f"Profile Variant: {variant}")
    st.text_area("Summary", summary, height=100, disabled=True)
    st.text_area("Resume Bullets", bullets, height=150, disabled=True)

    # 🔄 Usage Summary
    st.markdown("---")
    st.subheader("🔄 Usage Summary")
    usage_count = profile.get("usage_count", 0)
    credit_balance = profile.get("credit_balance", 0)
    free_remaining = max(0, 3 - usage_count)

    st.text(f"Free Uses Remaining: {free_remaining}")
    st.text(f"Paid Credits Remaining: {credit_balance}")

