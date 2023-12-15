# job_portal/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm, RecruiterProfileForm, JobSeekerProfileForm, JobPostForm
from .models import *



def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.user_type = request.POST.get('user_type')  # Set the user_type from the form
                user.save()
                login(request, user)
                return redirect('profile_creation')
        else:
            form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})
    else:
        return redirect('profile')



def login_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('profile')  # Redirect to the appropriate job page
            else:
                messages.error(request, 'Invalid username or password. Please try again.')

        return render(request, 'login.html')
    else:
        return redirect('profile')


def logout_view(request):
    logout(request)
    return redirect('login') # Redirect to the appropriate login page

@login_required
def job_post(request):
    user = request.user
    if user.is_authenticated:
        if user.user_type == 'Recruiter':
            if request.method == 'POST':
                form = JobPostForm(request.POST)
                if form.is_valid():
                    job_post = form.save(commit=False)
                    # Fetch the RecruiterProfile associated with the user
                    recruiter_profile = RecruiterProfile.objects.get(user_profile=user)
                    job_post.recruiter = recruiter_profile
                    job_post.save()
                    # Get selected skill IDs from the form data
                    selected_skill_ids = request.POST.getlist('skill_set')

                    # Convert the skill IDs to Skill instances
                    selected_skills = Skill.objects.filter(id__in=selected_skill_ids)

                    # Add the selected skills to the JobPost
                    job_post.skill_set.set(selected_skills)
                    return redirect('jobs')  # Redirect to the appropriate job page
            else:
                form = JobPostForm()
            return render(request, 'job_post.html', {'form': form})
        else:
            return HttpResponseForbidden("You do not have permission to post jobs.")
    else:
        return HttpResponseForbidden("You need to be logged in to post jobs.")

@login_required
def update_job(request, job_id):
    user = request.user

    # Ensure the user is authenticated and a recruiter
    if user.is_authenticated and user.user_type == 'Recruiter':
        # Get the job post instance
        job_post = get_object_or_404(JobPost, pk=job_id)

        # Ensure the logged-in recruiter is the owner of the job post
        if job_post.recruiter.user_profile == user:
            if request.method == 'POST':
                # Process the form submission for updating the job post
                form = JobPostForm(request.POST, instance=job_post)
                if form.is_valid():
                    form.save()
                    return redirect('jobs')  # Redirect to the appropriate job page
            else:
                # Render the form for updating the job post
                form = JobPostForm(instance=job_post)

            return render(request, 'update_job.html', {'form': form, 'job_post': job_post})
        else:
            return HttpResponseForbidden("You do not have permission to update this job.")
    else:
        return HttpResponseForbidden("You do not have permission to update this job.")
    

@login_required
def delete_job(request, job_id):
    user = request.user
    if user.is_authenticated and user.user_type == 'Recruiter':
        job_post = get_object_or_404(JobPost, pk=job_id)
        job_post.delete()
        return redirect('jobs')  # Redirect to the appropriate job page
    else:
        return HttpResponseForbidden("You do not have permission to delete this job.")




@login_required
def profile_creation(request):
    user_profile = request.user

    recruiter_profile = None
    job_seeker_profile = None

    if user_profile.user_type == 'Recruiter':
        try:
            recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
        except RecruiterProfile.DoesNotExist:
            pass

        form = RecruiterProfileForm(instance=recruiter_profile)

        if request.method == 'POST':
            form = RecruiterProfileForm(request.POST, instance=recruiter_profile)
            if form.is_valid():
                recruiter_profile = form.save(commit=False)
                recruiter_profile.user_profile = user_profile
                recruiter_profile.save()
                return redirect('jobs')

    elif user_profile.user_type == 'JobSeeker':
        try:
            job_seeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
        except JobSeekerProfile.DoesNotExist:
            pass

        form = JobSeekerProfileForm(instance=job_seeker_profile)

        if request.method == 'POST':
            form = JobSeekerProfileForm(request.POST, request.FILES, instance=job_seeker_profile)
            if form.is_valid():
                job_seeker_profile = form.save(commit=False)
                job_seeker_profile.user_profile = user_profile

                # Get selected skill IDs from the form data
                selected_skill_ids = request.POST.getlist('skills')

                # Convert the skill IDs to Skill instances
                selected_skills = Skill.objects.filter(id__in=selected_skill_ids)

                # Save the JobSeekerProfile with the selected skills
                job_seeker_profile.save()

                # Add the selected skills to the JobSeekerProfile
                job_seeker_profile.skills.set(selected_skills)

                return redirect('jobs')

    else:
        # Handle other user types
        pass

    return render(request, 'profile_creation.html', {'form': form})


@login_required
def profile_page(request):
    user_profile = request.user

    if user_profile.user_type == 'Recruiter':
        profile_data = get_object_or_404(RecruiterProfile, user_profile=user_profile)
        template_name = 'recruiter_profile.html'
    elif user_profile.user_type == 'JobSeeker':
        profile_data = get_object_or_404(JobSeekerProfile, user_profile=user_profile)
        template_name = 'jobseeker_profile.html'
    else:
        # Handle other user types or provide a default template
        profile_data = None
        template_name = 'default_profile.html'

    return render(request, template_name, {'profile_data': profile_data})






# job_portal

def job_list(request):
    categories = Category.objects.all()
    title_filter = request.GET.get('title', '')
    category_filter = request.GET.get('category', '')
    jobs = JobPost.objects.filter(title__icontains=title_filter)
    if category_filter:
        jobs = jobs.filter(category__id=category_filter)

    # Check if the user is a JobSeeker and has a JobSeekerProfile
    if request.user.is_authenticated and request.user.user_type == 'JobSeeker':
        try:
            job_seeker_profile = JobSeekerProfile.objects.get(user_profile=request.user)
        except JobSeekerProfile.DoesNotExist:
            # If the JobSeekerProfile does not exist, create one
            job_seeker_profile = JobSeekerProfile.objects.create(user_profile=request.user)
            # You can redirect to a profile creation page or do something else if needed

        # Extract job seeker's skills
        job_seeker_skills = job_seeker_profile.skills.all()
        # Find jobs that require at least one of the job seeker's skills
        matching_jobs = JobPost.objects.filter(skill_set__in=job_seeker_skills).distinct()
    else:
        job_seeker_profile = None
        matching_jobs = None

    return render(request, 'job_list.html', {'jobs': jobs, 'matching_jobs': matching_jobs, 'categories': categories, 'title_filter': title_filter, 'category_filter': category_filter})

# skill matched jobs only
def skill_matched_jobs(request):
    # Check if the user is a JobSeeker and has a JobSeekerProfile
    if request.user.is_authenticated and request.user.user_type == 'JobSeeker':
        try:
            job_seeker_profile = JobSeekerProfile.objects.get(user_profile=request.user)
        except JobSeekerProfile.DoesNotExist:
            # If the JobSeekerProfile does not exist, create one
            job_seeker_profile = JobSeekerProfile.objects.create(user_profile=request.user)
            # You can redirect to a profile creation page or do something else if needed

        # Extract job seeker's skills
        job_seeker_skills = job_seeker_profile.skills.all()
        # Find jobs that require at least one of the job seeker's skills
        matching_jobs = JobPost.objects.filter(skill_set__in=job_seeker_skills).distinct()
    else:
        job_seeker_profile = None
        matching_jobs = None

    return render(request, 'skill_matched_jobs.html', {'matching_jobs': matching_jobs, 'job_seeker_profile': job_seeker_profile})






@login_required
def job_detail(request, pk):
    job = get_object_or_404(JobPost, pk=pk)
    return render(request, 'job_detail.html', {'job': job})






@login_required
def apply_confirm_job(request, job_id):
    user = request.user
    if user.is_authenticated and user.user_type == 'JobSeeker':
        job_post = get_object_or_404(JobPost, pk=job_id)
        job_seeker_profile = JobSeekerProfile.objects.get(user_profile=user)

        if request.method == 'POST':
            # Process the confirmation form
            # For example, you can create an AppliedJob instance
            applied_job = AppliedJob(job_post=job_post, job_seeker_profile=job_seeker_profile)
            applied_job.save()
            return redirect('user_jobs')  # Redirect to the appropriate apllied job page
        else:
            return render(request, 'apply_confirm.html', {'job_post': job_post, 'job_seeker_profile': job_seeker_profile})
    else:
        return HttpResponseForbidden("You do not have permission to apply for this job.")
    


@login_required
def user_jobs(request):
    user_profile = request.user
    jobs = []

    if user_profile.user_type == 'Recruiter':
        # If the user is a recruiter, fetch and display the jobs they posted
        jobs = JobPost.objects.filter(recruiter__user_profile=user_profile)

        # Add a count of applications for each job
        for job in jobs:
            job.num_applications = AppliedJob.objects.filter(job_post=job).count()

    elif user_profile.user_type == 'JobSeeker':
        # If the user is a job seeker, fetch and display the jobs they applied to
        jobs = AppliedJob.objects.filter(job_seeker_profile__user_profile=user_profile)

    return render(request, 'user_jobs.html', {'jobs': jobs})



@login_required
def view_applications(request, job_id):
    job = get_object_or_404(JobPost, pk=job_id)
    applications = AppliedJob.objects.filter(job_post=job)

    print(job)  # Check if job is retrieved
    print(applications)  # Check if applications are retrieved

    return render(request, 'view_applications.html', {'job': job, 'applications': applications})






from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import os

@login_required
def download_resume(request, pk):
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user_profile__id=pk)
    
    # Check if the user trying to download the resume is a recruiter
    if not request.user.is_authenticated or request.user.user_type != 'Recruiter':
        raise PermissionDenied("You don't have permission to download resumes.")
    
    # Get the resume file path
    resume_path = job_seeker_profile.resume.path
    
    # Create the response and set the appropriate content type
    response = HttpResponse(content_type='application/pdf')  # Adjust content type based on resume type
    
    # Set the Content-Disposition header to force download
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(resume_path)}"'
    
    # Open and read the resume file
    with open(resume_path, 'rb') as resume_file:
        response.write(resume_file.read())
    
    return response