from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Resume, JobRole, MatchResult

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from PyPDF2 import PdfReader


# -------------------------
# Helper functions
# -------------------------

def extract_text_from_pdf(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def calculate_final_score(resume_text, job_skills, matched_skills):
    # ML similarity
    documents = [resume_text, job_skills]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    ml_score = cosine_similarity(
        tfidf_matrix[0:1], tfidf_matrix[1:2]
    )[0][0] * 100

    # Skill coverage
    total_skills = len(job_skills.split(","))
    skill_score = (len(matched_skills) / total_skills) * 100 if total_skills else 0

    # Final weighted score
    final_score = int((0.7 * ml_score) + (0.3 * skill_score))

    return final_score


def get_confidence_label(score):
    if score >= 75:
        return "Strong Match ✅", "green"
    elif score >= 50:
        return "Moderate Match ⚠️", "orange"
    else:
        return "Low Match ❌", "red"


# -------------------------
# Main view
# -------------------------

@login_required
def home(request):
    jobs = JobRole.objects.all()

    if request.method == "GET":
        return render(request, "core/home.html", {"jobs": jobs})

    # POST request
    job_id = request.POST.get("job_id")
    resume_text = request.POST.get("resume_text", "").strip()
    resume_file = request.FILES.get("resume_file")

    job = JobRole.objects.get(id=job_id)

    # If PDF uploaded, extract text
    if resume_file:
        resume_text = extract_text_from_pdf(resume_file)

    if not resume_text:
        return render(
            request,
            "core/home.html",
            {
                "jobs": jobs,
                "error": "Please upload a PDF or paste resume text."
            }
        )

    # Save resume
    resume = Resume.objects.create(
        user=request.user,
        resume_text=resume_text,
        resume_file=resume_file
    )

    resume_words = resume_text.lower()

    required_skills = [
        skill.strip().lower()
        for skill in job.required_skills.split(",")
    ]

    matched = []
    missing = []

    for skill in required_skills:
        if skill in resume_words:
            matched.append(skill)
        else:
            missing.append(skill)

    improvement_tips = []
    if missing:
        improvement_tips.append("Consider adding experience or keywords related to: " + ", ".join(missing))
        
    # FINAL SCORE + CONFIDENCE
    final_score = calculate_final_score(
        resume_text,
        job.required_skills,
        matched
    )

    confidence_label, confidence_color = get_confidence_label(final_score)

    # Save result
    MatchResult.objects.create(
        resume=resume,
        job_role=job,
        match_score=final_score
    )

    context = {
        "job_title": job.title,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": final_score,
        "confidence_label": confidence_label,
        "confidence_color": confidence_color,
        'improvement_tips': improvement_tips
    }

    return render(request, "core/result.html", context)
