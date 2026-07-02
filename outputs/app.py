import os
import streamlit as st
import matplotlib.pyplot as plt

from helper import rank_resumes

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
OUTPUT_DIR = BASE_DIR

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
        # Analyze resumes using helper.py
        # ---------------------------------------------------
        final_df = rank_resumes(job_description, uploaded_files)

        if final_df.empty:
            st.error("No resumes could be processed.")
            st.stop()

        # helper.py gives this column name
        if "resume_jd_similarity_percentage" in final_df.columns:
            final_df["resume_jd_similarity"] = final_df["resume_jd_similarity_percentage"]

        # ---------------------------------------------------
        # Save outputs
        # ---------------------------------------------------
        final_csv_path = os.path.join(OUTPUT_DIR, "final_candidate_ranking.csv")
        final_df.to_csv(final_csv_path, index=False)

        top_3 = final_df.head(3)[["rank", "candidate_name", "final_score", "recommendation"]]
        top_3.to_csv(os.path.join(OUTPUT_DIR, "top_3_candidates.csv"), index=False)

        # ---------------------------------------------------
        # Success message
        # ---------------------------------------------------
        st.success("Resume analysis completed successfully!")

        # ---------------------------------------------------
        # Quick Summary
        # ---------------------------------------------------
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

        with open(final_csv_path, "rb") as f:
            st.download_button(
                "⬇️ Download Full Ranking Report (CSV)",
                f,
                file_name="final_candidate_ranking.csv",
                mime="text/csv"
            )

        st.markdown("---")

        # ---------------------------------------------------
        # Top 3 Shortlisted Candidates
        # ---------------------------------------------------
        st.markdown("## ⭐ Top 3 Shortlisted Candidates")
        st.dataframe(top_3, use_container_width=True)

        st.markdown("---")

        # ---------------------------------------------------
        # Candidate Performance Charts
        # ---------------------------------------------------
        st.markdown("## 📊 Candidate Performance Charts")

        # Chart 1: Final Score
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.bar(final_df["candidate_name"], final_df["final_score"])
        ax1.set_title("Final Candidate Scores")
        ax1.set_xlabel("Candidate")
        ax1.set_ylabel("Final Score")
        plt.xticks(rotation=45)
        st.pyplot(fig1)
        fig1.savefig(os.path.join(OUTPUT_DIR, "final_score_chart.png"), bbox_inches="tight")

        # Chart 2: Skill Match Percentage
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.bar(final_df["candidate_name"], final_df["skill_match_percentage"])
        ax2.set_title("Skill Match Percentage")
        ax2.set_xlabel("Candidate")
        ax2.set_ylabel("Skill Match %")
        plt.xticks(rotation=45)
        st.pyplot(fig2)
        fig2.savefig(os.path.join(OUTPUT_DIR, "skill_match_chart.png"), bbox_inches="tight")

        # Chart 3: Resume-JD Similarity
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.bar(final_df["candidate_name"], final_df["resume_jd_similarity"])
        ax3.set_title("Resume-JD Similarity")
        ax3.set_xlabel("Candidate")
        ax3.set_ylabel("Similarity %")
        plt.xticks(rotation=45)
        st.pyplot(fig3)
        fig3.savefig(os.path.join(OUTPUT_DIR, "similarity_chart.png"), bbox_inches="tight")

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
                st.write(
                    f"**Matched Skills:** {', '.join(row['matched_skills']) if isinstance(row['matched_skills'], list) else row['matched_skills']}"
                )
                st.write(
                    f"**Missing Skills:** {', '.join(row['missing_skills']) if isinstance(row['missing_skills'], list) else row['missing_skills']}"
                )
                st.write(f"**Candidate Summary:** {row['candidate_summary']}")
                st.write(f"**Recruiter Note:** {row['recruiter_note']}")

        st.markdown("---")
        st.caption(
            "SmartHire AI | Resume Screening, Job Matching & Candidate Ranking using NLP + TF-IDF + Streamlit"
        )

    except Exception as e:
        st.error(f"An error occurred while processing resumes: {e}")