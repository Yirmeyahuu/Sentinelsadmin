from django.urls import path
from . import views

urlpatterns = [
    path('Registration/', views.StudentRegister, name='student_register'),
    path('Success/', views.RegisterSuccess, name='register_success'),
    path('check-student-id/', views.check_student_id, name='check_student_id'),
]