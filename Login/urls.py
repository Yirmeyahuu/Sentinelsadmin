from django.urls import path
from . import views

urlpatterns = [
    path('faculty-login/', views.Faculty_login_view, name='login'),
    path('superadmin-login/', views.Superadmin_login_view, name='superadmin_login'),


]