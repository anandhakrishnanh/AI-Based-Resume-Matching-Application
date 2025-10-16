# This script contains the frontend code to match the resumes to the job description and view the matches.
# importing the necessary libraries
import streamlit as st
import os

# importing the necessary components
from utils import rank_resumes
import Config


def view_matches_page():
    st.title("View Matches")
    st.subheader("View the matches between resumes and job descriptions")
    st.write("This page will display the matches between the uploaded resumes and job descriptions based on the ranking algorithm.")

    job_description_options = []
    for file in os.listdir(Config.JOB_DESCRIPTION_DIRECTORY):
        if file.endswith(".txt"):
            job_description_options.append(file)

    # Choose from the available job descriptions
    job_description = st.selectbox("Select Job Description", options=job_description_options)
    if job_description:
        job_description_path = os.path.join(Config.JOB_DESCRIPTION_DIRECTORY, job_description)
        with open(job_description_path, "r") as jd_file:
            jd_text = jd_file.read()

        st.markdown("### Job Description")
        st.text_area("Job Description Text", value=jd_text, height=200, disabled=True)

        if st.button("Rank Resumes"):
            with st.spinner("Ranking resumes..."):
                ranked_resumes = rank_resumes.score_directory(job_description_path, Config.RESUME_DIRECTORY)

                st.success("Resumes ranked successfully!")

                # Take the top N resumes to display
                top_resumes = ranked_resumes[:Config.SHOW_TOP_N_RESUMES]

                # Only use resumes with score above the threshold
                top_score_resumes = [item for item in top_resumes if item["score"] >= Config.SCORE_THRESHOLD]

                if not top_score_resumes:
                    st.warning(f"No resumes found with a score above the threshold of {Config.SCORE_THRESHOLD}.")
                    with st.expander("🔍 Raw JSON Data"):
                        st.json(top_resumes)
                    return

                for idx, item in enumerate(top_score_resumes, 1):
                    with st.expander(f"#{idx}. {item['candidate']} — Score: {item['score']}"):
                        st.markdown(f"**Matched Skills:** {', '.join(item['matched_skills'])}")

                        if item["missing_must_haves"]:
                            st.markdown(f"**❗ Missing Must-Haves:** {', '.join(item['missing_must_haves'])}")
                        else:
                            st.markdown("**✅ All must-have skills are present.**")

                        with st.expander("📚 Evidence Sentences"):
                            for sentence in item["evidence_sentences"]:
                                st.markdown(f"- {sentence}")

                        if item.get("notes"):
                            st.info(f"📝 Notes: {item['notes']}")

                with st.expander("🔍 Raw JSON Data"):
                    st.json(top_resumes)