from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Sentinels_login_view, name='sentinels_login'),
    path('faculty-logout/', views.Faculty_logout_view, name='faculty_logout'),  # Add logout URL
    path("superadminlogout/", views.superadmin_logout, name="superadmin_logout"),
    path('logout/', views.Faculty_logout_view, name='sentinels_logout'),
]