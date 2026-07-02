import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from helper import (
    load_job_description,
    process_multiple_resumes,
    rank_candidates,
    save_results
)

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="SmartHire AI",
    page_icon="📄",
    layout="wide"
)

# ---------------------------------------------------
# Title / Intro
# ---------------------------------------------------
st.title("📄 SmartHire AI — Resume Screening & Candidate Ranking System")
st.write(
    "SmartHire AI helps recruiters screen multiple resumes against a Job Description (JD), "
    "calculate match scores, and rank candidates using skill matching + resume similarity."
)

st.markdown("---")

# ---------------------------------------------------
# Paths
# ---------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # outputs/
PROJECT_ROOT = os.path.dirname(BASE_DIR)                # SmartHire_AI/
SAMPLE_DIR = os.path.join(PROJECT_ROOT, "data", "sample_resume")

SAMPLE_JD_PATH = os.path.join(SAMPLE_DIR, "job_description.txt")
OUTPUT_DIR = BASE_DIR   # outputs folder itself

# ---------------------------------------------------
# Session state for Job Description
# ---------------------------------------------------
if "job_description" not in st.session_state:
    st.session_state.job_description = ""

# ---------------------------------------------------
# Sample JD Checkbox
# ---------------------------------------------------
use_sample_jd = st.checkbox("Use sample Job Description from project files")

if use_sample_jd:
    try:
        with open(SAMPLE_JD_PATH, "r", encoding="utf-8") as f:
            st.session_state.job_description = f.read()
        st.success("Sample Job Description loaded successfully.")
    except Exception as e:
        st.error(f"Could not load sample Job Description: {e}")

# ---------------------------------------------------
# Step 1: Job Description Input
# ---------------------------------------------------
st.markdown("## 📝 Step 1: Enter Job Description")

job_description = st.text_area(
    "Paste the Job Description here",
    value=st.session_state.job_description,
    height=250,
    placeholder="Example: Looking for a Data Analyst with Python, SQL, Excel, Tableau, Machine Learning..."
)

# Keep session state updated if user edits text manually
st.session_state.job_description = job_description

st.markdown("---")

# ---------------------------------------------------
# Step 2: Resume Upload
# ---------------------------------------------------
st.markdown("## 📂 Step 2: Upload Candidate Resumes (.txt only)")

uploaded_files = st.file_uploader(
    "Upload multiple resume files",
    type=["txt"],
    accept_multiple_files=True
)

# ---------------------------------------------------
# Analyze Button
# ---------------------------------------------------
if st.button("🚀 Analyze Resumes"):

    if not job_description.strip():
        st.warning("Please enter a Job Description or use the sample Job Description checkbox.")
        st.stop()

    if not uploaded_files:
        st.warning("Please upload at least one resume file.")
        st.stop()

    try:
        # ---------------------------------------------------
        # Save uploaded resumes temporarily inside outputs/temp_resumes
        # ---------------------------------------------------
        temp_resume_dir = os.path.join(OUTPUT_DIR, "temp_uploaded_resumes")
        os.makedirs(temp_resume_dir, exist_ok=True)

        resume_file_paths = []

        for uploaded_file in uploaded_files:
            save_path = os.path.join(temp_resume_dir, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            resume_file_paths.append(save_path)

        # ---------------------------------------------------
        # Process resumes
        # ---------------------------------------------------
        processed_df = process_multiple_resumes(job_description, resume_file_paths)

        if processed_df.empty:
            st.error("No resumes could be processed.")
            st.stop()

        # ---------------------------------------------------
        # Rank candidates
        # ---------------------------------------------------
        final_df = rank_candidates(processed_df)

        # ---------------------------------------------------
        # Save CSV / charts / reports
        # ---------------------------------------------------
        save_results(processed_df, final_df, output_dir=OUTPUT_DIR)

        # ---------------------------------------------------
        # Quick Summary
        # ---------------------------------------------------
        st.success("Resume analysis completed successfully!")

        st.markdown("## 📌 Quick Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Resumes", len(final_df))

        with col2:
            st.metric("Top Candidate", final_df.iloc[0]["candidate_name"])

        with col3:
            st.metric("Top Score", f"{final_df.iloc[0]['final_score']:.2f}")

        st.markdown("---")

        # ---------------------------------------------------
        # Final Candidate Ranking
        # ---------------------------------------------------
        st.markdown("## 🏆 Final Candidate Ranking")
        st.dataframe(final_df, use_container_width=True)

        final_csv_path = os.path.join(OUTPUT_DIR, "final_candidate_ranking.csv")
        if os.path.exists(final_csv_path):
            with open(final_csv_path, "rb") as f:
                st.download_button(
                    "⬇️ Download Full Ranking Report (CSV)",
                    f,
                    file_name="final_candidate_ranking.csv",
                    mime="text/csv"
                )

        st.markdown("---")

        # ---------------------------------------------------
        # Top 3 Candidates
        # ---------------------------------------------------
        st.markdown("## ⭐ Top 3 Shortlisted Candidates")
        top_3 = final_df.head(3)[["rank", "candidate_name", "final_score", "recommendation"]]
        st.dataframe(top_3, use_container_width=True)

        st.markdown("---")

        # ---------------------------------------------------
        # Charts Section
        # ---------------------------------------------------
        st.markdown("## 📊 Candidate Performance Charts")

        # 1. Final Score Chart
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.bar(final_df["candidate_name"], final_df["final_score"])
        ax1.set_title("Final Candidate Scores")
        ax1.set_xlabel("Candidate")
        ax1.set_ylabel("Final Score")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        # 2. Skill Match Chart
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.bar(final_df["candidate_name"], final_df["skill_match_percentage"])
        ax2.set_title("Skill Match Percentage")
        ax2.set_xlabel("Candidate")
        ax2.set_ylabel("Skill Match %")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        # 3. Resume Similarity Chart
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.bar(final_df["candidate_name"], final_df["resume_jd_similarity"])
        ax3.set_title("Resume-JD Similarity")
        ax3.set_xlabel("Candidate")
        ax3.set_ylabel("Similarity %")
        plt.xticks(rotation=45)
        st.pyplot(fig3)

        st.markdown("---")

        # ---------------------------------------------------
        # Candidate Detailed Analysis
        # ---------------------------------------------------
        st.markdown("## 📋 Candidate Detailed Analysis")

        for _, row in final_df.iterrows():
            with st.expander(
                f"Rank {row['rank']} — {row['candidate_name']} | "
                f"Score: {row['final_score']:.2f} | {row['recommendation']}"
            ):
                st.write(f"**Skill Match Percentage:** {row['skill_match_percentage']:.2f}%")
                st.write(f"**Resume-JD Similarity:** {row['resume_jd_similarity']:.2f}%")
                st.write(f"**Matched Skills:** {row['matched_skills']}")
                st.write(f"**Missing Skills:** {row['missing_skills']}")
                st.write(f"**Recruiter Note:** {row['recruiter_note']}")

        st.markdown("---")
        st.caption(
            "SmartHire AI | Resume Screening, Job Matching & Candidate Ranking using NLP + TF-IDF + Streamlit"
        )

    except Exception as e:
        st.error(f"An error occurred while processing resumes: {e}")