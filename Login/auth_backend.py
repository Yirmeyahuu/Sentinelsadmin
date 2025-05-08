from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from firebase_admin import firestore

db = firestore.client()

class FirestoreBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        if not username or not password:
            return None

        # Fetch faculty document from Firestore
        doc_ref = db.collection("Authorized Faculty").document(username)
        doc = doc_ref.get()

        if doc.exists:
            faculty_data = doc.to_dict()
            # Check if the password matches the default password
            if password == "welcomeadmin":  # Replace with hashed password check if needed
                # Create or get a Django user object
                user, created = User.objects.get_or_create(username=username)
                user.first_name = faculty_data.get("first_name", "")
                user.last_name = faculty_data.get("last_name", "")
                user.save()
                return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None