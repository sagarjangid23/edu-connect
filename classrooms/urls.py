from django.urls import path
from .views import (
    home,
    display_teachers,
    display_students,
    generate_certificate,
    verify_certificate,
)

urlpatterns = [
    path("", home, name="home"),
    path("teachers", display_teachers, name="teachers"),
    path("students", display_students, name="students"),
    path("generate-certificate/", generate_certificate, name="generate_certificate"),
    path("verify-certificate/", verify_certificate, name="verify_certificate"),
]
