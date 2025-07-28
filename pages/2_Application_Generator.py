# ... [imports and setup unchanged] ...

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


def ensure_profile_keys(profile):
    defaults = {
        "usage_count": 0,
        "paid_credits": 0,
        "tone": "Default",
        "pending_payment": False
    }
    for key, default in defaults.items():
        if key not in profile:
            profile[key] = default
    return profile

def can_generate_application(profile):
    return profile.get("usage_count", 0) < 3 or profile.get("paid_credits", 0) > 0

def increment_usage(profile):
    if profile.get("usage_count", 0) < 3:
        profile["usage_count"] += 1
    else:
        profile["paid_credits"] = max(profile.get("paid_credits", 0) - 1, 0)
    return profile

# --- Load User Profile ---
query_params = st.query_params
email = st.text_input("Enter your email to load config", key="email_jobgen")

profile = None
if email:
    profile = load_user_profile(email)

    if not profile:
        st.warning("⚠️ No user profile found. Please check the email or create one.")
        st.stop()

    profile = ensure_profile_keys(profile)

    # Handle Stripe redirect after successful payment
    if query_params.get("paid") and query_params.get("paid")[0] == "1":
        if profile.get("pending_payment", False):
            profile["paid_credits"] += 10
            profile["pending_payment"] = False
            save_user_profile(email, profile)
            st.success("✅ Payment successful. 10 credits added.")
            st.experimental_set_query_params(email=email)  # clean the URL
        else:
            st.warning("⚠️ Payment already processed or invalid.")

    if not can_generate_application(profile):
        st.error("❌ You've used all 3 free applications and have no remaining credits.")
        st.markdown("### 💰 Purchase More Credits")
        st.markdown("Each cover letter generation costs 1 credit. Buy 10 for $5 AUD.")
        if st.button("🔓 Buy 10 Credits ($5 AUD)"):
            profile["pending_payment"] = True
            save_user_profile(email, profile)
            url = create_checkout_session(email)
            st.markdown(f"[Click here if not redirected]({url})")
            st.markdown(f"""<meta http-equiv=\"refresh\" content=\"0; URL='{url}'\" />""", unsafe_allow_html=True)
        st.stop()

    # --- Session Defaults ---
    defaults = {
        "job_title": "",
        "company": "",
        "job_ad_text": "",
        "recent_news": "",
        "strategy_docs": "",
        "job_objectives": "",
        "improvement_notes": ""
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    render_job_inputs()
    render_news_section(normalize_company_name, fetch_company_news_cached)
    render_optional_inputs()
    render_profile_view(profile)

    # --- Generate Cover Letter ---
    if st.button("📝 Generate Cover Letter"):
        if not can_generate_application(profile):
            st.warning("⚠️ No more credits. Please purchase more.")
            st.stop()

        job_text = st.session_state.get("job_ad_text", "")
        if job_text.strip():
            if not st.session_state["job_objectives"]:
                st.session_state["job_objectives"] = extract_job_objectives(job_text)
        else:
            st.warning("⚠️ Please paste a job ad before generating a cover letter.")
            st.stop()

        st.session_state["generated_text"] = generate_cover_letter(
            job_title=st.session_state["job_title"],
            company=st.session_state["company"],
            job_ad_text=st.session_state["job_ad_text"],
            job_objectives=st.session_state["job_objectives"],
            cv_summary=profile.get("cv_summary", ""),
            resume_bullets=profile.get("resume_bullets", ""),
            tone=profile.get("tone", "Default"),
            news   =st.session_state["recent_news"],
            strategy=st.session_state["strategy_docs"]
            )

        profile = increment_usage(profile)
        save_user_profile(email, profile)
        st.success("✅ Cover letter generated!")

    # --- Show Output ---
    if "generated_text" in st.session_state:
        st.markdown("### ✉️ Your Cover Letter")
        st.text_area("Output", value=st.session_state["generated_text"], height=300, key="output", disabled=False)

def create_checkout_session(email):
    import stripe
    import os
    from dotenv import load_dotenv

    load_dotenv()
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=email,
        line_items=[{
            "price_data": {
                "currency": "aud",
                "product_data": {"name": "10 Job Application Credits"},
                "unit_amount": 500,
            },
            "quantity": 1,
        }],
        success_url=f"https://jobagent.streamlit.app/Application_Generator?email={email}&paid=1",
        cancel_url="https://jobagent.streamlit.app/Application_Generator",
    )

    return session.url
