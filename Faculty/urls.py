from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    #URLS FOR FACULTY HOME PAGE
    path("homepage/", views.Faculty_home, name="home-page"),

    #URLS FOR STUDENT MANAGEMENT PAGE
    path("Student-list/", views.student_list, name="faculty-student-list"),
    path("add/", views.add_student, name="add_student"),
    path("check-student-id/", views.check_student_id, name="check_student_id"),
    path("Archived-Students/", views.archived_students_list_page, name="archived_students_list"),
    path('edit/<str:student_id>/', views.edit_student, name='edit_student'),
    path('Verify-students/', views.Verify_Student, name='verify-students'),
    path('Student-Data/', views.studentData, name='student-data'),
    path('Student-status/', views.faculty_student_status, name='faculty-student-status'),
    path('delete-archived-student/<str:student_id>/', views.faculty_delete_archived_student, name='faculty_delete_archived_student'),
    path('student-data/modal/<str:student_id>/', views.studentDataModal, name='student-data-modal'),
    path('Restore-student/', views.restoreStudent, name ="restore-student"),

    path('accept-student/<str:student_id>/', views.accept_student, name='accept_student'),
    path('reject-student/<str:student_id>/', views.reject_student, name='reject_student'),

    # Add this to your urlpatterns
    path('account/', views.faculty_account, name='faculty-account'),
    path('faculty/edit/', views.edit_faculty_account, name='edit_faculty_account'),
    
    #URLS FOR ACTIVITY PAGE
    path("Activity-list/", views.Faculty_activity_page, name='faculty-activity-page'),
    path('save-activity-deadline/', views.saveActivityDeadline, name='save-activity-deadline'),
    path('remove-deadline/', views.remove_deadline, name='remove-deadline'), 
    path('get-late-completions/<str:task_title>/', views.get_late_completions, name='get-late-completions'),

    
    #URLS FOR STUDENT DASHBOARD
    path('Student-progress/', views.student_progress, name='student-progress'),

    path("move-student/", views.move_student, name="faculty_move_student"),

    path('Tier/Novice/', views.novice_tier, name='novice-tier'),
    path('Tier/Junior/', views.junior_tier, name='junior-tier'),
    path('Tier/Senior/', views.senior_tier, name='senior-tier'),


    # Student Import/Export URLs
    path('students/export/csv/', views.export_student_csv, name='export_student_csv'),
    path('students/export/excel/', views.export_student_excel, name='export_student_excel'),
    path('students/import/', views.import_student, name='import_student'),
    path('students/template/csv/', views.download_student_csv_template, name='download_student_csv_template'),
    path('students/template/excel/', views.download_student_excel_template, name='download_student_excel_template'),


    # Developers Section
    path('Developers/', views.facultyDevinnovateSection, name="devinnovate-section"),

    # URL for uploading faculty profile image
    path('upload-profile-image/', views.upload_faculty_profile_image, name='upload_faculty_profile_image'),
    path('remove-profile-image/', views.remove_faculty_profile_image, name='remove_faculty_profile_image'),
]