from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_common_view),
    path("submit_feedback/", views.submit_feedback),
    path("register/", views.reg_common_view),
    path("register/reg_common_submit", views.reg_common_submit),
    path("register/reg_stud_submit", views.reg_stud_submit),
    path("register/reg_fac_submit", views.reg_fac_submit),
    path("register/reg_comp_submit", views.reg_comp_submit),
    path("login_common_submit", views.login_common_submit),
    # path("register/reg_admin_submit", views.reg_admin_submit),
]