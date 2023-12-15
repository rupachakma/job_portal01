from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Skill)
admin.site.register(Category)
admin.site.register(RecruiterProfile)
admin.site.register(JobSeekerProfile)
admin.site.register(JobPost)
admin.site.register(AppliedJob)