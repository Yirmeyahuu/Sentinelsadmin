from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    #This is the space url for login. It is the root url for the login app.
    path('', include("Login.urls")),
    
    #This is the URl's for the main apps. Serves as the root urls for the apps.
    path('Faculty/', include("Faculty.urls")),
    path('Superadmin/', include("SuperAdmin.urls")),
    path('Student/', include("Student.urls")),
]
