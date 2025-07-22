import streamlit as st

st.set_page_config(
    page_title="Operator Agent",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Operator Agent Home")
st.markdown("Welcome to the OperatorGPT application engine.")

st.markdown("---")

st.subheader("Quick Actions")
st.markdown("- Use the sidebar to open **User Config** and save your profile.")
st.markdown("- Use future pages (Job Generator, History, etc.) as they're added.")

st.info("This page will eventually be your dashboard, with history, quick links, and job scraping tools.")
