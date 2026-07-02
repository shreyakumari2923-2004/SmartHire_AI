import re
import nltk
import pandas as pd

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# NLTK setup
# -----------------------------
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

stop_words = set(stopwords.words("english"))
ps = PorterStemmer()

# -----------------------------
# Master Skill List
# -----------------------------
SKILL_LIST = [
    "python",
    "sql",
    "excel",
    "tableau",
    "power bi",
    "pandas",
    "numpy",
    "matplotlib",
    "scikit-learn",
    "machine learning",
    "deep learning",
    "data analysis",
    "data visualization",
    "statistics",
    "communication",
    "problem solving",
    "html",
    "css",
    "javascript",
    "java",
    "c++",
    "mysql",
    "github"
]

# -----------------------------
# Read text file
# -----------------------------
def read_text_file(file):
    """
    Reads uploaded TXT file and returns text content.
    """
    return file.read().decode("utf-8")


# -----------------------------
# Clean text
# -----------------------------
def clean_text(text):
    """
    Cleans text by:
    - converting to lowercase
    - removing special characters
    - tokenizing
    - removing stopwords
    - applying stemming
    """
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    words = nltk.word_tokenize(text)

    cleaned_words = []
    for word in words:
        if word not in stop_words and word.isalnum():
            cleaned_words.append(ps.stem(word))

    return " ".join(cleaned_words)


# -----------------------------
# Extract skills
# -----------------------------
def extract_skills(text, skill_list=SKILL_LIST):
    """
    Extracts skills from a text using the predefined skill list.
    """
    text = text.lower()
    found_skills = []

    for skill in skill_list:
        if skill.lower() in text:
            found_skills.append(skill)

    return list(set(found_skills))


# -----------------------------
# Matched skills
# -----------------------------
def get_matched_skills(resume_skills, jd_skills):
    """
    Returns common skills between resume and JD.
    """
    return list(set(resume_skills).intersection(set(jd_skills)))


# -----------------------------
# Missing skills
# -----------------------------
def get_missing_skills(resume_skills, jd_skills):
    """
    Returns skills required in JD but missing in resume.
    """
    return list(set(jd_skills) - set(resume_skills))


# -----------------------------
# Resume-JD similarity
# -----------------------------
def calculate_resume_jd_similarity(resume_text, job_description_text):
    """
    Calculates cosine similarity between resume and JD using TF-IDF.
    """
    text_list = [job_description_text, resume_text]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(text_list)

    similarity_score = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return similarity_score


# -----------------------------
# Recommendation tag
# -----------------------------
def get_recommendation_tag(score):
    """
    Returns recommendation label based on final score.
    """
    if score >= 75:
        return "Highly Suitable"
    elif score >= 50:
        return "Moderately Suitable"
    else:
        return "Low Match"


# -----------------------------
# Candidate summary
# -----------------------------
def generate_candidate_summary(candidate_name, score, recommendation,
                               matched_count, missing_count):
    """
    Generates candidate summary text.
    """
    if recommendation == "Highly Suitable":
        return (
            f"{candidate_name} is a strong fit for the role with a high overall score of {score}. "
            f"The candidate matches {matched_count} important job skills and has only {missing_count} key skills missing."
        )

    elif recommendation == "Moderately Suitable":
        return (
            f"{candidate_name} is a reasonably suitable candidate with a score of {score}. "
            f"The candidate matches {matched_count} job-relevant skills but still lacks {missing_count} important skills."
        )

    else:
        return (
            f"{candidate_name} is currently a low match for the role with a score of {score}. "
            f"The candidate matches only {matched_count} relevant skills and is missing {missing_count} important job skills."
        )


# -----------------------------
# Missing skill insight
# -----------------------------
def generate_missing_skill_insight(missing_skills):
    """
    Generates insight based on missing skills.
    """
    if len(missing_skills) == 0:
        return "No major skill gaps detected for this role."
    elif len(missing_skills) <= 3:
        return f"Candidate is missing a few important skills: {', '.join(missing_skills)}."
    else:
        top_missing = missing_skills[:5]
        return (
            "Candidate lacks several important skills required for the role, "
            f"such as: {', '.join(top_missing)}."
        )


# -----------------------------
# Recruiter note
# -----------------------------
def generate_recruiter_note(candidate_name, final_score,
                            recommendation, missing_skill_insight):
    """
    Generates recruiter-style final note.
    """
    return (
        f"Candidate {candidate_name} received a final SmartHire score of {final_score} "
        f"and is classified as '{recommendation}'. {missing_skill_insight}"
    )


# -----------------------------
# Main ranking function
# -----------------------------
def rank_resumes(job_description, uploaded_files):
    """
    Main SmartHire pipeline:
    - reads uploaded resumes
    - cleans text
    - extracts skills
    - calculates similarity
    - calculates final score
    - ranks candidates
    - returns final ranking dataframe
    """
    cleaned_jd = clean_text(job_description)
    jd_skills = extract_skills(job_description)

    candidate_data = []

    for file in uploaded_files:
        resume_text = read_text_file(file)
        candidate_name = file.name.replace(".txt", "")
        cleaned_resume = clean_text(resume_text)

        resume_skills = extract_skills(resume_text)
        matched_skills = get_matched_skills(resume_skills, jd_skills)
        missing_skills = get_missing_skills(resume_skills, jd_skills)

        skill_match_count = len(matched_skills)
        total_jd_skills = len(jd_skills)

        if total_jd_skills == 0:
            skill_match_percentage = 0
        else:
            skill_match_percentage = (skill_match_count / total_jd_skills) * 100

        similarity_score = calculate_resume_jd_similarity(
            cleaned_resume,
            cleaned_jd
        )
        similarity_percentage = similarity_score * 100

        final_score = (0.6 * skill_match_percentage) + (0.4 * similarity_percentage)
        final_score = round(final_score, 2)

        recommendation = get_recommendation_tag(final_score)

        candidate_summary = generate_candidate_summary(
            candidate_name,
            final_score,
            recommendation,
            len(matched_skills),
            len(missing_skills)
        )

        missing_skill_insight = generate_missing_skill_insight(missing_skills)

        recruiter_note = generate_recruiter_note(
            candidate_name,
            final_score,
            recommendation,
            missing_skill_insight
        )

        candidate_data.append({
            "candidate_name": candidate_name,
            "resume_text": resume_text,
            "resume_skills": resume_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "matched_skill_count": len(matched_skills),
            "missing_skill_count": len(missing_skills),
            "skill_match_percentage": round(skill_match_percentage, 2),
            "resume_jd_similarity_percentage": round(similarity_percentage, 2),
            "final_score": final_score,
            "recommendation": recommendation,
            "candidate_summary": candidate_summary,
            "recruiter_note": recruiter_note
        })

    ranking_df = pd.DataFrame(candidate_data)

    ranking_df = ranking_df.sort_values(
        by="final_score",
        ascending=False
    ).reset_index(drop=True)

    ranking_df["rank"] = ranking_df.index + 1

    return ranking_df