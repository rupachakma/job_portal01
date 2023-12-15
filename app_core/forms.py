# job_portal/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(label='Join as a:', choices=[('', '-------'),('JobSeeker', 'JobSeeker'),('Recruiter', 'Recruiter')], widget=forms.Select(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Enter strong password',widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Repeat password',widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['username', 'display_name', 'email', 'password1', 'password2', 'user_type']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['company_name', 'address']

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['skills', 'resume']
        widgets = {
            'skills': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['title', 'openings', 'category', 'description', 'skill_set']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'openings': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'skill_set': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
