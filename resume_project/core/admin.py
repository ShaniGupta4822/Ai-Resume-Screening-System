from django.contrib import admin
from .models import Resume, JobRole, MatchResult

admin.site.register(Resume)
admin.site.register(JobRole)
admin.site.register(MatchResult)
