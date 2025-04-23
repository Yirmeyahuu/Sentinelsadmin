from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("homepage/", views.Faculty_home, name="home-page"),
    path("Student-list", views.student_list, name="student-list"),
    path("add/", views.add_student, name="add_student"),  # Ensure this matches the form action URL
    path("archive/<str:student_id>/", views.archive_student, name="archive_student"),
    path("archive/", views.archived_student_list, name="archive-page"),
    path("restore/<str:student_id>/", views.restore_student, name="restore_student"),
    path('edit/<str:student_id>/', views.edit_student, name='edit_student')
]