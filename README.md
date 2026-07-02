# 📄 SmartHire AI — Resume Screening & Candidate Ranking System

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?logo=streamlit)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?logo=scikitlearn)
![NLP](https://img.shields.io/badge/NLP-Resume%20Screening-green)

SmartHire AI is an NLP-powered **resume screening and candidate ranking system** that helps recruiters evaluate multiple resumes against a given **Job Description (JD)**. It uses **skill matching + TF-IDF based similarity scoring** to rank candidates and generate recruiter-friendly candidate insights.

---

# 🚀 Features

- Upload and analyze **multiple candidate resumes**
- Match resumes against a **job description**
- Extract **resume skills**
- Identify **matched skills** and **missing skills**
- Calculate **resume-job similarity score**
- Generate **final candidate ranking**
- Show **Top 3 shortlisted candidates**
- Provide **candidate summary + recruiter note**
- Download full ranking report as **CSV**
- Interactive **Streamlit web app UI**

---

# 🧠 Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **NumPy**
- **Matplotlib**
- **NLTK**
- **Scikit-learn**
- **TF-IDF Vectorization**
- **Cosine Similarity**

---

# 📂 Project Structure

```bash
SmartHire_AI/
│
├── data/
│   └── sample_resume/
│       ├── job_description.txt
│       ├── resume_1.txt
│       ├── resume_2.txt
│       ├── resume_3.txt
│       ├── resume_4.txt
│       └── resume_5.txt
│
├── images/
│   ├── home1.png
│   ├── home2.png
│   ├── home3.png
│   ├── ranking.png
│   ├── chart1.png
│   ├── chart2.png
│   ├── chart3.png
│   ├── shortlist.png
│   ├── analysis1.png
│   ├── analysis2.png
│   └── detailedanalysis.png
│
├── notebooks/
│
├── outputs/
│   ├── app.py
│   ├── helper.py
│   ├── requirements.txt
│   ├── README.md
│   ├── .gitignore
│   ├── raw_resume_data.csv
│   ├── processed_resume_data.csv
│   ├── resume_skill_analysis.csv
│   ├── resume_similarity_analysis.csv
│   ├── final_candidate_ranking.csv
│   ├── final_candidate_ranking_with_tags.csv
│   ├── smarthire_final_report.csv
│   ├── top_3_candidates.csv
│   ├── final_score_chart.png
│   ├── skill_match_chart.png
│   ├── similarity_chart.png
│   └── top_3_candidates_chart.png
│
├── README.md
└── requirements.txt
```
# 📸 App Screenshots

## 1. Home Page
![Home Page](./images/home1.png)

---

## 2. Final Candidate Ranking
![Final Candidate Ranking](./images/ranking.png)

---

## 3. Candidate Performance Charts
![Chart 1](./images/chart1.png)

![Chart 2](./images/chart2.png)

![Chart 3](./images/chart3.png)

---

## 4. Top 3 Shortlisted Candidates
![Top 3 Shortlisted Candidates](./images/shortlist.png)

---

## 5. Candidate Detailed Analysis
![Detailed Candidate Analysis](./images/detailedanalysis.png)
