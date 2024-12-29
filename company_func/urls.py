from django.urls import path
from . import views

urlpatterns = [
    # path("stu/", views.reg_common_view),
    path("home", views.company_home),
    path("postjob", views.company_postjob),
    path("postjob_submit", views.company_postjob_submit),
    path("ong_recruitments", views.company_ong_recruitments),
    path("college_history", views.company_college_history),
]