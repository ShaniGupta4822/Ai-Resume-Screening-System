from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume_text = models.TextField(blank=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class JobRole(models.Model):
    title = models.CharField(max_length=100)
    required_skills = models.TextField()

    def __str__(self):
        return self.title


class MatchResult(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE)
    match_score = models.IntegerField()

    def __str__(self):
        return f"{self.resume.user.username} - {self.job_role.title}"
