# Contains the scripts and functions used to display the resume summary page in the frontend.
# importing the necessary libraries
import streamlit as st
import os

# importing the necessary components
import Config

def resume_summary_page():
    st.title("Resume Summary")
    st.subheader("View the summary of uploaded resumes")
    st.write("This page will display the summaries of the resumes that have been uploaded to the system.")

    resume_summary_dir = Config.RESUME_SUMMARY

    try:
        summary_files = [f for f in os.listdir(resume_summary_dir) if f.endswith("_summary.txt")]
    except FileNotFoundError:
        st.error(f"Directory {resume_summary_dir} not found. Please upload a resume first.")
        return

    if not summary_files:
        st.info("No resume summaries found. Please upload a resume first.")
        return

    selected_file = st.selectbox("Select a resume summary to view:", summary_files)

    if selected_file:
        summary_path = os.path.join(resume_summary_dir, selected_file)
        with open(summary_path, "r") as file:
            summary_content = file.read()
            st.markdown(summary_content, unsafe_allow_html=True)
