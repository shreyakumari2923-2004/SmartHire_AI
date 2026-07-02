import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from helper import rank_resumes

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="SmartHire AI",
    page_icon="📄",
    layout="wide"
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.title("📌 SmartHire AI")
st.sidebar.write("Resume Screening & Candidate Ranking System")

st.sidebar.markdown("### How to use")
st.sidebar.write("1. Paste the Job Description")
st.sidebar.write("2. Upload multiple resume TXT files")
st.sidebar.write("3. Click **Analyze Resumes**")
st.sidebar.write("4. View ranking, charts and candidate reports")

st.sidebar.markdown("---")
st.sidebar.markdown("### Tech Stack")
st.sidebar.write("- Python")
st.sidebar.write("- Streamlit")
st.sidebar.write("- NLP")
st.sidebar.write("- TF-IDF")
st.sidebar.write("- Scikit-learn")

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("📄 SmartHire AI — Resume Screening & Candidate Ranking System")

st.write(
    """
    SmartHire AI helps recruiters screen multiple resumes against a Job Description (JD),
    calculate candidate-job match scores, and rank candidates using **skill matching + resume similarity**.
    """
)

st.markdown("---")

# --------------------------------------------------
# Load sample JD if available
# --------------------------------------------------
sample_jd_path = os.path.join("..", "data", "sample_resume", "job_description.txt")

sample_jd_text = ""
if os.path.exists(sample_jd_path):
    with open(sample_jd_path, "r", encoding="utf-8") as f:
        sample_jd_text = f.read()

use_sample_jd = st.checkbox("Use sample Job Description from project files")

# --------------------------------------------------
# Job Description Input
# --------------------------------------------------
st.subheader("📝 Step 1: Enter Job Description")

default_jd = sample_jd_text if use_sample_jd else ""

job_description = st.text_area(
    "Paste the Job Description here",
    value=default_jd,
    height=250,
    placeholder="Example: Looking for a Data Analyst with Python, SQL, Excel, Tableau, Machine Learning..."
)

# --------------------------------------------------
# Resume Upload
# --------------------------------------------------
st.subheader("📂 Step 2: Upload Candidate Resumes (.txt only)")

uploaded_files = st.file_uploader(
    "Upload multiple resume files",
    type=["txt"],
    accept_multiple_files=True
)

if uploaded_files:
    st.write("### Uploaded Resume Files")
    for file in uploaded_files:
        st.write(f"- {file.name}")

# --------------------------------------------------
# Analyze Button
# --------------------------------------------------
if st.button("🚀 Analyze Resumes"):

    if not job_description.strip():
        st.error("Please enter a Job Description before analyzing resumes.")

    elif not uploaded_files:
        st.error("Please upload at least one resume file.")

    else:
        uploaded_resume_files = list(uploaded_files)

        with st.spinner("Analyzing resumes... Please wait..."):
            ranking_df = rank_resumes(job_description, uploaded_resume_files)

        if ranking_df.empty:
            st.error("No candidate data was generated. Please check the uploaded files.")
        else:
            st.success("Resume analysis completed successfully!")

            st.markdown("---")

            # --------------------------------------------------
            # Quick Summary Metrics
            # --------------------------------------------------
            st.subheader("📊 Quick Summary")

            total_candidates = len(ranking_df)
            top_candidate = ranking_df.iloc[0]["candidate_name"]
            top_score = ranking_df.iloc[0]["final_score"]
            avg_score = round(ranking_df["final_score"].mean(), 2)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Candidates", total_candidates)
            col2.metric("Top Candidate", top_candidate)
            col3.metric("Top Score", top_score)
            col4.metric("Average Score", avg_score)

            st.markdown("---")

            # --------------------------------------------------
            # Final Candidate Ranking Table
            # --------------------------------------------------
            st.subheader("🏆 Final Candidate Ranking")

            display_ranking_df = ranking_df[[
                "rank",
                "candidate_name",
                "final_score",
                "recommendation",
                "skill_match_percentage",
                "resume_jd_similarity_percentage"
            ]].copy()

            display_ranking_df.columns = [
                "Rank",
                "Candidate Name",
                "Final Score",
                "Recommendation",
                "Skill Match %",
                "Resume-JD Similarity %"
            ]

            st.dataframe(display_ranking_df, use_container_width=True)

            # Download CSV
            csv_data = ranking_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download Full Ranking Report (CSV)",
                data=csv_data,
                file_name="smarthire_candidate_ranking.csv",
                mime="text/csv"
            )

            st.markdown("---")

            # --------------------------------------------------
            # Charts Section
            # --------------------------------------------------
            st.subheader("📈 Candidate Performance Charts")

            # Chart 1: Final Score Chart
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            ax1.bar(ranking_df["candidate_name"], ranking_df["final_score"])
            ax1.set_title("Final Candidate Scores")
            ax1.set_xlabel("Candidate")
            ax1.set_ylabel("Final Score")
            plt.xticks(rotation=45)
            st.pyplot(fig1)

            # Chart 2: Skill Match %
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            ax2.bar(ranking_df["candidate_name"], ranking_df["skill_match_percentage"])
            ax2.set_title("Skill Match Percentage")
            ax2.set_xlabel("Candidate")
            ax2.set_ylabel("Skill Match %")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

            # Chart 3: Resume-JD Similarity %
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            ax3.bar(ranking_df["candidate_name"], ranking_df["resume_jd_similarity_percentage"])
            ax3.set_title("Resume-JD Similarity Percentage")
            ax3.set_xlabel("Candidate")
            ax3.set_ylabel("Similarity %")
            plt.xticks(rotation=45)
            st.pyplot(fig3)

            st.markdown("---")

            # --------------------------------------------------
            # Top 3 Shortlisted Candidates
            # --------------------------------------------------
            st.subheader("⭐ Top 3 Shortlisted Candidates")

            top_3_df = ranking_df.head(3)

            for i in range(len(top_3_df)):
                candidate = top_3_df.iloc[i]
                st.markdown(
                    f"""
                    ### #{candidate['rank']} — {candidate['candidate_name']}
                    - **Final Score:** {candidate['final_score']}
                    - **Recommendation:** {candidate['recommendation']}
                    - **Skill Match %:** {candidate['skill_match_percentage']}
                    - **Resume Similarity %:** {candidate['resume_jd_similarity_percentage']}
                    """
                )

            st.markdown("---")

            # --------------------------------------------------
            # Candidate Detailed Analysis
            # --------------------------------------------------
            st.subheader("📋 Candidate Detailed Analysis")

            for i in range(len(ranking_df)):
                candidate = ranking_df.iloc[i]

                with st.expander(
                    f"Rank {candidate['rank']} — {candidate['candidate_name']} | "
                    f"Score: {candidate['final_score']} | {candidate['recommendation']}"
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### Candidate Overview")
                        st.write(f"**Candidate Name:** {candidate['candidate_name']}")
                        st.write(f"**Rank:** {candidate['rank']}")
                        st.write(f"**Final Score:** {candidate['final_score']}")
                        st.write(f"**Recommendation:** {candidate['recommendation']}")
                        st.write(f"**Skill Match %:** {candidate['skill_match_percentage']}")
                        st.write(f"**Resume Similarity %:** {candidate['resume_jd_similarity_percentage']}")

                    with col2:
                        st.markdown("### Skill Analysis")
                        st.write(f"**Matched Skill Count:** {candidate['matched_skill_count']}")
                        st.write(f"**Missing Skill Count:** {candidate['missing_skill_count']}")

                    st.markdown("### Resume Skills")
                    st.write(candidate["resume_skills"])

                    st.markdown("### Matched Skills")
                    st.write(candidate["matched_skills"])

                    st.markdown("### Missing Skills")
                    st.write(candidate["missing_skills"])

                    st.markdown("### Candidate Summary")
                    st.write(candidate["candidate_summary"])

                    st.markdown("### Recruiter Note")
                    st.write(candidate["recruiter_note"])

            st.markdown("---")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.caption("SmartHire AI | Resume Screening, Job Matching & Candidate Ranking using NLP + TF-IDF + Streamlit")