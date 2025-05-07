from django.contrib import messages  # Corrected import for messages
from django.shortcuts import render, redirect
from firebase_admin import credentials, firestore
import firebase_admin

db = firestore.client()
# Initialize Firebase Admin SDK

# Create your views here.
def Faculty_login_view(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        password = request.POST.get('faculty_password')

        # Look for the faculty document
        users_ref = db.collection('Authorized Faculty')
        query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()

        if query:
            faculty_doc = query[0]
            faculty_data = faculty_doc.to_dict()

            # Check if the password matches the default password
            if password == "welcomeadmin":
                # Successful login logic
                return redirect('home-page')  # Update this path as needed
            else:
                messages.error(request, "Incorrect password. Please use the default password: 'welcomeadmin'.")
        else:
            messages.error(request, "Faculty ID not found.")

    return render(request, 'Login/faculty-login.html')

def Superadmin_login_view(request):
    return render(request, 'Login/superadmin-login.html')

