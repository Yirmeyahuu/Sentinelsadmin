from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #URLS FOR FACULTY HOME PAGE
    path("homepage/", views.Faculty_home, name="home-page"),
    # path('sticky-container/', views.sticky_container_partial, name='sticky_container_partial'),

    
    #URLS FOR STUDENT MANAGEMENT PAGE
    path("Student-list/", views.student_list, name="faculty-student-list"),
    path("add/", views.add_student, name="add_student"),
    path("Archived-Students/", views.archived_students_list_page, name="archived_students_list"),
    # path("restore/<str:student_id>/", views.restore_student, name="restore_student"),
    path('edit/<str:student_id>/', views.edit_student, name='edit_student'),
    path('Verify-students/', views.Verify_Student, name='verify-students'),
    path('Student-status/', views.faculty_student_status, name='faculty-student-status'),

    path('accept-student/<str:student_id>/', views.accept_student, name='accept_student'),
    path('reject-student/<str:student_id>/', views.reject_student, name='reject_student'),

    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('save-activity-deadline/', views.saveActivityDeadline, name='save-activity-deadline'),

    # Add this to your urlpatterns
    path('account/', views.faculty_account, name='faculty-account'),
    path('faculty/edit/', views.edit_faculty_account, name='edit_faculty_account'),

    path('remove-deadline/', views.remove_deadline, name='remove-deadline'),    
    
    #URLS FOR ACTIVITY PAGE
    path("Activity-list/", views.Faculty_activity_page, name='faculty-activity-page'),
    path('save-activity-deadline/', views.saveActivityDeadline, name='save-activity-deadline'),
    
    #URLS FOR STUDENT DASHBOARD
    path('Student-progress/', views.student_progress, name='student-progress'),

    path("move-student/", views.move_student, name="faculty_move_student"),

    path('Tier/Novice/', views.novice_tier, name='novice-tier'),
    path('Tier/Junior/', views.junior_tier, name='junior-tier'),
    path('Tier/Senior/', views.senior_tier, name='senior-tier'),

    path('Help/', views.facultyHelp, name='faculty-help'),

]