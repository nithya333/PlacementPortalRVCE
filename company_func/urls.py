from django.urls import path
from . import views

urlpatterns = [
    # path("stu/", views.reg_common_view),
    path("home", views.company_home),
    path("postjob", views.company_postjob),
    path("postjob_submit", views.company_postjob_submit),
    path("oa_int_link", views.company_oa_int_link),
    path("results", views.company_results),
    path("ong_recruitments", views.company_ong_recruitments),
    path("past_recruitments", views.company_past_recruitments),
    path('ong_recruitments/vmore/<str:job_id>/', views.company_ong_recruitments_vmore, name='company_job'),
]