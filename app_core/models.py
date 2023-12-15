# job_portal/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models



class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class UserProfile(AbstractUser):
    display_name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20)  # 'Recruiter' or 'JobSeeker'
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return self.username

class RecruiterProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.user_profile.username

class JobSeekerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill)
    resume = models.FileField(upload_to='resumes/')

    def __str__(self):
        return self.user_profile.username

class JobPost(models.Model):
    recruiter = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    openings = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    skill_set = models.ManyToManyField(Skill)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class AppliedJob(models.Model):
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    job_seeker_profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_seeker_profile.user_profile.display_name} applied for {self.job_post.title}"




