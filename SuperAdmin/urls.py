from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("homepage/", views.Superadmin_Home, name="Superadmin-homepage"),  # Fixed faculty page view
    
    path("Activity-list/", views.Superadmin_activity_page, name='Superadmin_ActivityList'),
    path('update-game-trigger/', views.update_game_trigger, name='update_game_trigger'),
    path('update-tier-lock/', views.update_tier_lock, name='update_tier_lock'),

    path("Faculty-list/", views.Faculty_list, name="FacultyList"),  # Fixed faculty page view #faculty-page
    path("add/", views.add_faculty, name="add_faculty"),
    path("Faculty-Archived/", views.Archived_faculty_list, name="Faculty_Archived"),
    path("archive/<str:faculty_id>/", views.Faculty_Archive, name="archive_faculty"),
    path('archived-faculty/delete/<str:faculty_id>/', views.delete_archived_faculty, name='delete_archived_faculty'),

    path("restore/<str:faculty_id>/", views.restore_faculty, name="restore_faculty"),
    path('faculty/edit/<str:faculty_id>/', views.edit_faculty, name='edit_faculty'),
    path('faculty/move/', views.move_faculty, name='move_faculty'),
    path('Faculty-status/', views.Faculty_Status, name='Faculty_status'),

    path('Student-status/', views.Superadmin_Student_Status, name='superadmin-student-status'),
    path('Student-list/', views.Superadmin_Student_List, name='student-list'),
    path('student/move/', views.superadmin_move_student, name='move_student'),
    path("Student-Archived/", views.Superadmin_Student_Archive, name="superadmin_student_archived"),
    path('archived-student/delete/<str:student_id>/', views.delete_archived_student, name='delete_archived_student'),


    path('faculty/export-csv/', views.export_faculty_csv, name='export_faculty_csv'),
    path('faculty/import-csv/', views.import_faculty_csv, name='import_faculty_csv'),
    path('faculty/download-template/', views.download_faculty_csv_template, name='download_faculty_csv_template'),
    path('faculty/export-excel/', views.export_faculty_excel, name='export_faculty_excel'),
    path('faculty/download-excel-template/', views.download_faculty_excel_template, name='download_faculty_excel_template'),
    
]
