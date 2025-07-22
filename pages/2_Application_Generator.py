from modules.fetch_news import fetch_company_news
from modules.parse_job_ad import extract_job_objectives
from modules.profile_utils import (
    load_user_profile,
    increment_usage,
    save_application_to_history,
    can_generate_application
)
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import os
import urllib.parse

# Load environment and init OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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


email = st.text_input("Enter your email to load config", key="email_jobgen")

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
        st.error("❌ You've reached your weekly limit. Purchase credits or upgrade to continue.")
        st.stop()

    for key in ["job_title", "company", "job_ad_text", "recent_news", "strategy_docs"]:
        if key not in st.session_state:
            st.session_state[key] = ""

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

    if st.button("📰 Fetch Company News"):
        company_name = normalize_company_name(st.session_state.get("company", "").strip())
        st.caption("Use exact legal name (e.g. 'JPMorgan Chase').")
        if not company_name:
            st.error("❌ Company name required.")
        else:
            try:
                news = fetch_company_news(company_name)
                if "No relevant articles" in news or "Error" in news:
                    st.error(news)
                else:
                    st.session_state.auto_news_summary = news
                    st.subheader("📌 Fetched News")
                    st.markdown(news.replace('\n', '  \n'))
            except Exception as e:
                st.error(f"❌ News fetch failed: {e}")

    if "job_objectives" in st.session_state:
        st.markdown("### ✅ Parsed Job Objectives")
        st.json(st.session_state.job_objectives)

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

    if st.session_state.job_title and st.session_state.company:
        news_link = generate_news_url(st.session_state.company, st.session_state.job_title)
        st.markdown("### 🔍 Manual News Search")
        st.markdown(f"[Google News →]({news_link})", unsafe_allow_html=True)

    st.markdown("### 🧠 Optional Context")
    st.session_state.recent_news = st.text_area("Paste relevant media releases/news", value=st.session_state.recent_news)
    st.session_state.strategy_docs = st.text_area("Paste annual reports/strategy docs", value=st.session_state.strategy_docs)

    st.markdown("### 👤 From Your Profile")
    tone = profile.get("preferred_tone", "professional")
    summary = profile.get("cv_summary", "")
    bullets = profile.get("resume_bullets", "")
    variant = profile.get("profile_variant", "Leader")

    st.text(f"Tone: {tone}")
    st.text(f"Profile Variant: {variant}")
    st.text_area("Summary", summary, height=100, disabled=True)
    st.text_area("Resume Bullets", bullets, height=150, disabled=True)

    def generate_application(prompt_override=None):
        job_ad_segment = (
            f"Full Job Description: {st.session_state.job_ad_text}" if st.session_state.job_ad_text.strip()
            else "Note: No job ad was provided. Write based on typical responsibilities for this role."
        )

        prompt = prompt_override or f"""
You are a high-performance job application strategist. Write for a candidate who is outcome-obsessed, senior, and knows how to lead, sell, or execute. Avoid all fluff. Use the job ad and any contextual info to craft a focused, confident application with strategic bite.

[JOB DETAILS]
Title: {st.session_state.job_title}
Company: {st.session_state.company}
{job_ad_segment}

[OPTIONAL INSIGHTS]
News/Media: {st.session_state.recent_news or st.session_state.get('auto_news_summary', '')}
Strategy Docs: {st.session_state.strategy_docs}

[PROFILE]
Summary: {summary}
Resume Bullets: {bullets}
Tone: {tone}
Variant: {variant}

[INSTRUCTIONS]
- Make the candidate sound like the obvious hire — results-driven, aligned, already thinking about impact.
- Integrate any relevant company activity (expansion, leadership shifts, strategy).
- Avoid vague statements. Every line should either prove value, show insight, or suggest alignment.
- Write like a peer, not a supplicant.
- Do NOT use phrases like “I believe”, “I would love the opportunity”, or “thank you for considering”.

Format:
[RESUME]
<resume blurb>

[COVER LETTER]
<cover letter>
""".strip()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You write elite-level applications for hard-charging professionals. Your voice is sharp, concise, and persuasive. Assume the reader is busy and skeptical — win them over fast."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        text_output = response.choices[0].message.content
        resume_text = text_output.split("[COVER LETTER]")[0].replace("[RESUME]", "").strip()
        cover_letter_text = text_output.split("[COVER LETTER]")[1].strip()
        return resume_text, cover_letter_text

    if st.button("⚙️ Generate Application"):
        try:
            increment_usage(email)
            resume_text, cover_letter_text = generate_application()

            outputs = {
                "resume": resume_text,
                "cover_letter": cover_letter_text
            }

            save_application_to_history(email, st.session_state.job_title, st.session_state.company, outputs)
            st.success("✅ Application generated!")

            with st.expander("📄 Resume"):
                st.code(resume_text, language="markdown")
                resume_feedback = st.text_area("💡 Suggest improvements", key="resume_improve")
                if st.button("🔁 Improve Resume"):
                    improved_prompt = f"""
You are improving a resume blurb based on user feedback.

Current resume content:
{resume_text}

User feedback:
{resume_feedback}

Only rewrite the [RESUME] section. Format:
[RESUME]
<new resume>
"""
                    new_resume, _ = generate_application(prompt_override=improved_prompt + "\n\n[COVER LETTER]")
                    st.code(new_resume, language="markdown")
                st.download_button("⬇️ Download Resume", resume_text, file_name="resume.txt")

            with st.expander("✉️ Cover Letter"):
                st.code(cover_letter_text, language="markdown")
                letter_feedback = st.text_area("💡 Suggest improvements", key="letter_improve")
                if st.button("🔁 Improve Cover Letter"):
                    improved_prompt = f"""
You are improving a cover letter based on user feedback.

Current cover letter:
{cover_letter_text}

User feedback:
{letter_feedback}

Only rewrite the [COVER LETTER] section. Format:
[COVER LETTER]
<new letter>
"""
                    _, new_letter = generate_application(prompt_override=improved_prompt + "\n\n[RESUME]")
                    st.code(new_letter, language="markdown")
                st.download_button("⬇️ Download Cover Letter", cover_letter_text, file_name="cover_letter.txt")

        except Exception as e:
            st.error(f"❌ Application generation failed: {e}")
