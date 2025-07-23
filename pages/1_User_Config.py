import streamlit as st
from modules.profile_utils import (
    load_user_profile,
    save_user_profile,
    increment_usage,
    can_generate_application,
)

st.set_page_config(page_title="User Config", page_icon="🧠")
st.title("🧠 User Profile Configuration")
st.markdown("Fill in your details to personalise job applications.")

email = st.text_input("Email (used to load/save profile)")

if email:
    profile = load_user_profile(email)

    # Resume input
    st.markdown("**Paste Your Resume**")
    profile["resume"] = st.text_area("Resume Text", value=profile.get("resume", ""), height=300)

    profile["goal"] = st.text_input("Career Goal", value=profile.get("goal", ""))
    profile["industries"] = st.text_input("Target Industries (comma-separated)", value=profile.get("industries", ""))
    profile["roles"] = st.text_input("Target Roles (comma-separated)", value=profile.get("roles", ""))
    profile["companies"] = st.text_input("Target Companies (comma-separated)", value=profile.get("companies", ""))
    
    profile["preferred_tone"] = st.selectbox(
        "Preferred Tone",
        ["professional", "friendly", "persuasive"],
        index=["professional", "friendly", "persuasive"].index(profile.get("preferred_tone", "professional"))
    )

    profile["profile_variant"] = st.selectbox(
        "Profile Style",
        ["Leader", "Visionary", "Entrepreneur", "Fixer", "Team Builder"],
        index=0
    )

    profile["subscription_status"] = st.selectbox(
        "Subscription Tier",
        ["free", "pay_per_use", "subscribed"],
        index=["free", "pay_per_use", "subscribed"].index(profile.get("subscription_status", "free"))
    )

    st.markdown(f"**Usage Count:** {profile.get('usage_count', 0)}")

    if st.button("💾 Save Profile"):
        increment_usage(email)
        save_user_profile(email, profile)
        st.success("Profile saved!")

    with st.expander("🔍 Debug Preview"):
        st.json(profile)
