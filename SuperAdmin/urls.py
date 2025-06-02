from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("homepage/", views.Superadmin_Home, name="Superadmin-homepage"),  # Fixed faculty page view
    
    path("Activity-list/", views.activity_page, name='Superadmin_ActivityList'),
    
    path("Faculty-list/", views.Faculty_list, name="FacultyList"),  # Fixed faculty page view #faculty-page


    
    path("add/", views.add_faculty, name="add_faculty"),  # Ensure this matches the form action URL
    path("archive/<str:faculty_id>/", views.archive_faculty, name="archive_faculty"),
    path("ArchivedFaculty/", views.Archived_faculty_list, name="Faculty-Archived"),
    path("restore/<str:faculty_id>/", views.restore_faculty, name="restore_faculty"),
    path('faculty/edit/<str:faculty_id>/', views.edit_faculty, name='edit_faculty'),
    path('faculty/move/', views.move_faculty, name='move_faculty'),
    path('Faculty-status/', views.Faculty_status, name='faculty-status'),


    path('student-status/', views.student_status, name='student-status'),


]