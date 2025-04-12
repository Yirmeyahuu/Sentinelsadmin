from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('superadmin-login/', views.superadmin_login_view, name='superadmin_login'),
]