from django.urls import path
from . import views

urlpatterns = [
    # path("stu/", views.reg_common_view),
    path("home", views.company_home),
    path("postjob", views.company_postjob),
    path("postjob_submit", views.company_postjob_submit),
    path("ong_recruitments", views.company_ong_recruitments),
    path('ong_recruitments/vmore/<str:job_id>/', views.company_ong_recruitments_vmore, name='company_job'),
    path("college_history", views.company_college_history),
]