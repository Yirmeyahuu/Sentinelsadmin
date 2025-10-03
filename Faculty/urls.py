from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #URLS FOR FACULTY HOME PAGE
    path("homepage/", views.Faculty_home, name="home-page"),

    #URLS FOR STUDENT MANAGEMENT PAGE
    path("Student-list/", views.student_list, name="faculty-student-list"),
    path("add/", views.add_student, name="add_student"),
    path("Archived-Students/", views.archived_students_list_page, name="archived_students_list"),
    path('edit/<str:student_id>/', views.edit_student, name='edit_student'),
    path('Verify-students/', views.Verify_Student, name='verify-students'),
    path('Student-status/', views.faculty_student_status, name='faculty-student-status'),

    path('accept-student/<str:student_id>/', views.accept_student, name='accept_student'),
    path('reject-student/<str:student_id>/', views.reject_student, name='reject_student'),

    # Add this to your urlpatterns
    path('account/', views.faculty_account, name='faculty-account'),
    path('faculty/edit/', views.edit_faculty_account, name='edit_faculty_account'),
    
    #URLS FOR ACTIVITY PAGE
    path("Activity-list/", views.Faculty_activity_page, name='faculty-activity-page'),
    path('save-activity-deadline/', views.saveActivityDeadline, name='save-activity-deadline'),
    path('remove-deadline/', views.remove_deadline, name='remove-deadline'), 

    
    #URLS FOR STUDENT DASHBOARD
    path('Student-progress/', views.student_progress, name='student-progress'),

    path("move-student/", views.move_student, name="faculty_move_student"),

    path('Tier/Novice/', views.novice_tier, name='novice-tier'),
    path('Tier/Junior/', views.junior_tier, name='junior-tier'),
    path('Tier/Senior/', views.senior_tier, name='senior-tier'),


    # Student Import/Export URLs
    path('students/export/csv/', views.export_student_csv, name='export_student_csv'),
    path('students/export/excel/', views.export_student_excel, name='export_student_excel'),
    path('students/import/', views.import_student_csv, name='import_student_csv'),
    path('students/template/csv/', views.download_student_csv_template, name='download_student_csv_template'),
    path('students/template/excel/', views.download_student_excel_template, name='download_student_excel_template'),
]