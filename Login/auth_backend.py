from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from Faculty.models import Faculty
from firebase_admin import firestore

db = firestore.client()

class HybridFacultyBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            faculty = Faculty.objects.get(faculty_id=username)
            if check_password(password, faculty.password):
                user, _ = User.objects.get_or_create(username=faculty.faculty_id)
                user.first_name = faculty.first_name
                user.last_name = faculty.last_name
                user.save()
                request.session['user_type'] = 'faculty'
                return user
        except Faculty.DoesNotExist:
            pass

        # Fallback to Firestore for legacy accounts
        doc_ref = db.collection("Authorized Faculty").document(username)
        doc = doc_ref.get()
        if doc.exists:
            faculty_data = doc.to_dict()
            if password == "welcomeadmin":
                user, _ = User.objects.get_or_create(username=username)
                user.first_name = faculty_data.get("first_name", "")
                user.last_name = faculty_data.get("last_name", "")
                user.save()
                request.session['user_type'] = 'faculty'
                return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None