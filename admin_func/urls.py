from django.urls import path
from . import views

urlpatterns = [
    path("home", views.head_home),
    path("allot_slots", views.head_allot_slots),
    path("track_placements", views.head_track_placements),
    path("review_feedback", views.head_review_feedback),
]