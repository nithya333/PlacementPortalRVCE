from django.urls import path
from . import views

urlpatterns = [
    # path("stu/", views.reg_common_view),
    path("home", views.student_home),
    path("profile", views.student_profile),
    path("applied", views.student_applied),
    path('applied/vmore/<int:job_id>/', views.student_applied_vmore, name='student_job'),
    path("new", views.student_new),
]