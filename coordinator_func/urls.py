from django.urls import path
from . import views

urlpatterns = [
    # path("stu/", views.reg_common_view),
    path("home", views.coordinator_home),
    path("shortlist", views.coordinator_shortlist),
    path("shortlist_selected", views.coordinator_shortlist_selected),
    path('shortlist/vmore/<str:job_id>/', views.coordinator_shortlist_vmore, name='coordinator_job'),
    path("track", views.coordinator_track),
]