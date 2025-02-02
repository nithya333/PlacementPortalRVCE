from django.urls import path
from . import views

urlpatterns = [
    path("sample", views.get_sample),
    path("verify_user", views.verify_user),
    path("new_jobs", views.new_jobs),
    path("applied_jobs", views.applied_jobs),
]