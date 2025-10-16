# This will act as the landing page for the web application.
# importing the necessary libraries
import streamlit as st


# importing the necessary components
from frontend.upload_resume import upload_resume_page
from frontend.upload_job_description import upload_job_description_page
from frontend.resume_summary_page import resume_summary_page
from frontend.view_matches_page import view_matches_page

st.title("AI Based Resume Matching System")
st.subheader("Welcome to the AI Based Resume Matching System")
st.write("This web application allows you to upload resumes and job descriptions, and uses AI to match candidates to job roles based on their skills and experience.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to:",
        ["Home", "Upload Resume", "Upload Job Description", "View Matches", "Resume Summary"],
        index=0,
        key="nav_page",
    )

if page == "Home":
    st.info("Use the sidebar to navigate.")

elif page == "Upload Resume":
    upload_resume_page()

elif page == "Resume Summary":
    resume_summary_page()

elif page == "Upload Job Description":
    upload_job_description_page()

elif page == "View Matches":
    view_matches_page()
