from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.reg_common_view),
    path("register/reg_common_submit", views.reg_common_submit),
    path("register/reg_stud_submit", views.reg_stud_submit),
]