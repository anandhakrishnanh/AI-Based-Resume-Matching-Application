# This page will be used to upload job descriptions and store them as text files in the system
# importing the necessary libraries
import streamlit as st
import uuid
import os

# importing the necessary components
from utils import utils
import Config

def upload_job_description_page():
    st.title("Upload Job Description")
    st.subheader("Upload your job description to the system")
    st.write("Please type the job description in the input field. The job description will be processed and stored in the system for matching with resumes.")

    utils.create_required_directories()

    job_description = st.text_input("Job Description")
    job_description_dir = Config.JOB_DESCRIPTION_DIRECTORY
    if st.button("Upload Job Description"):
        if job_description.strip() == "":
            st.error("❌ Job description cannot be empty.")
        else:
            # Save the job description to a text file
            job_description_file = job_description_dir + f"/job_description_{uuid.uuid4().hex}.txt"
            with open(job_description_file, "w") as f:
                f.write(job_description)

            st.success("✅ Job description uploaded successfully!")
            st.caption(f"Saved to: {job_description_file}")

    # Show what’s currently in the directory
    with st.expander("View job descriptions folder"):
        job_description_dir_path = Config.JOB_DESCRIPTION_DIRECTORY
        files = sorted([f for f in os.listdir(job_description_dir_path) if f.endswith('.txt')])
        if files:
            for index, file in enumerate(files):
                with open(os.path.join(job_description_dir_path, file), "r") as f:
                    content = f.read()
                st.write(f"**Job Description #{index}:**")
                st.write(content)
                st.write("---")
        else:
            st.write("No job descriptions found yet.")