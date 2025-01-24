from django.urls import path
from . import views

urlpatterns = [
    # path("stu/", views.reg_common_view),
    path("home", views.student_home),
    path("profile", views.student_profile),
    path("profile_submit", views.student_profile_submit),
    path("applied", views.student_applied),
    path("past_applied", views.student_past_applied),
    path('applied/vmore/<str:job_id>/', views.student_applied_vmore, name='student_job'),
    path("new", views.student_new),
    path("apply/<str:job_id>/", views.student_new_apply, name='student_job'),
    path("spc_shortlist", views.spc_shortlist),
    path("spc_shortlist_selected", views.spc_shortlist_selected),
    path('spc_shortlist/vmore/<str:job_id>/', views.spc_shortlist_vmore, name='spc_duty'),
    path("fetchpdf/<str:u_id>/", views.export_student_resume),
    path('parse_resume/', views.parse_resume)
]