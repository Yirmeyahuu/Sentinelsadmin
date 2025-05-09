from django.urls import path
from . import views

urlpatterns = [
    path('Registration/', views.StudentRegister, name='student_register'),
    path('Success/', views.RegisterSuccess, name='register_success'),  # Add this line to include the success URL    
]