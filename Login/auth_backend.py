from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from Faculty.models import Faculty

class HybridFacultyBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            faculty = Faculty.objects.get(faculty_id=username)
            
            # Check if using default password
            if password == "welcomeadmin" and not faculty.password_changed:
                # Allow login with default password
                user, _ = User.objects.get_or_create(username=faculty.faculty_id)
                user.first_name = faculty.first_name
                user.last_name = faculty.last_name
                user.save()
                request.session['user_type'] = 'faculty'
                request.session['faculty_id'] = faculty.faculty_id
                request.session['requires_password_change'] = True
                return user
            
            # Check hashed password for changed passwords
            elif faculty.check_password(password):
                user, _ = User.objects.get_or_create(username=faculty.faculty_id)
                user.first_name = faculty.first_name
                user.last_name = faculty.last_name
                user.save()
                request.session['user_type'] = 'faculty'
                request.session['faculty_id'] = faculty.faculty_id
                request.session['requires_password_change'] = faculty.is_default_password()
                return user
                
        except Faculty.DoesNotExist:
            pass

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None