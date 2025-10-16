# This page will be used to upload resumes to the system.
# importing the necessary libraries
import streamlit as st
from streamlit import session_state
import os
from pathlib import Path

# importing the necessary components
from utils import utils, summary_generation
import Config

def upload_resume_page():
    st.title("Upload Resume")
    st.subheader("Upload your resume to the system")
    st.write("Please upload your resume in PDF format. The resume will be processed and stored in the system for matching with job descriptions.")

    utils.create_required_directories()

    resume_dir = Path(Config.RESUME_DIRECTORY)
    resume_dir.mkdir(parents=True, exist_ok=True)

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="resume_uploader")

    # Save the file if uploaded
    if uploaded_file is not None:
        with st.spinner("Parsing uploaded resume..."):
            save_path = resume_dir / uploaded_file.name
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            resume_text = utils.extract_text_from_pdf(save_path)
            resume_summary = summary_generation.summarize_text(resume_text)
            resume_summary_path = os.path.join(Config.RESUME_SUMMARY, uploaded_file.name + "_summary.txt")
            with open(resume_summary_path, "w") as summary_file:
                summary_file.write(resume_summary)

            st.success(f"✅ Resume '{uploaded_file.name}' uploaded successfully!")
            st.caption(f"Saved to: {save_path.resolve()}")

    # Show what’s currently in the directory
    with st.expander("View resumes folder"):
        files = sorted([p.name for p in resume_dir.glob("*.pdf")])
        if files:
            st.write("Resumes found:")
            st.write(files)
        else:
            st.write("No resumes found yet.")