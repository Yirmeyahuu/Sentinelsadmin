from django.urls import path
from . import views

urlpatterns = [
    path('faculty-login/', views.Faculty_login_view, name='faculty_login'),
    path('superadmin-login/', views.Superadmin_login_view, name='superadmin_login'),
    path('faculty-logout/', views.Faculty_logout_view, name='faculty_logout'),  # Add logout URL
    path("superadminlogout/", views.superadmin_logout, name="superadmin_logout"),
]