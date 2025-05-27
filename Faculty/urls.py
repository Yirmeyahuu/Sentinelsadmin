from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #URLS FOR FACULTY HOME PAGE
    path("homepage/", views.Faculty_home, name="home-page"),
    
    #URLS FOR STUDENT MANAGEMENT PAGE
    path("Student-list/", views.student_list, name="student-list"),
    path("add/", views.add_student, name="add_student"),
    path("archive/<str:student_id>/", views.archive_student, name="archive_student"),
    path("Archived-Students/", views.archived_student_list, name="archive-page"),
    path("restore/<str:student_id>/", views.restore_student, name="restore_student"),
    path('edit/<str:student_id>/', views.edit_student, name='edit_student'),
    path('Verify-students/', views.Verify_Student, name='verify-students'),

    path('accept-student/<str:student_id>/', views.accept_student, name='accept_student'),
    path('reject-student/<str:student_id>/', views.reject_student, name='reject_student'),

    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('save-activity-deadline/', views.saveActivityDeadline, name='save-activity-deadline'),

    # Add this to your urlpatterns
    path('account/', views.faculty_account, name='faculty-account'),

    path('remove-deadline/', views.remove_deadline, name='remove-deadline'),    
    
    #URLS FOR ACTIVITY PAGE
    path("Activity-list/", views.activity_page, name='activities-page'),
    
    #URLS FOR STUDENT DASHBOARD
    path("dashboard/", views.student_dashboard, name="student-dashboard"),


    path("move-student/", views.move_student, name="move_student"),


]