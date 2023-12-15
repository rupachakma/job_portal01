from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('profile_creation/', profile_creation, name='profile_creation'),
    path('logout/', logout_view, name='logout'),
    path('job_post/', job_post, name='job_post'),
    path('update_job/<int:job_id>/', update_job, name='update_job'),
    path('delete_job/<int:job_id>/', delete_job, name='delete_job'),
    path('profile/', profile_page, name='profile'),
    path('', job_list, name='jobs'),
    path('jobs/<int:pk>/', job_detail, name='job_detail'),
    path('skill_matched_jobs/', skill_matched_jobs, name='skill_matched_jobs'),
    path('apply_confirm/<int:job_id>/', apply_confirm_job, name='apply'),
    path('user_jobs/', user_jobs, name='user_jobs'),
    path('view_applications/<int:job_id>/', view_applications, name='view_applications'),
    path('download_resume/<int:pk>/', download_resume, name='download_resume'),
]
