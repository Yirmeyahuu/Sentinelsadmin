from django.contrib import messages  # Corrected import for messages
from django.shortcuts import render, redirect
from firebase_admin import credentials, firestore
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from Login.decorators import faculty_required, superadmin_required

db = firestore.client()
# Initialize Firebase Admin SDK

# Create your views here.


def Faculty_login_view(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        password = request.POST.get('faculty_password')

        users_ref = db.collection('Authorized Faculty')
        query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()

        if query:
            faculty_doc = query[0]
            faculty_data = faculty_doc.to_dict()
            faculty_password = faculty_data.get('faculty_password')

            # If faculty has set a password, use it. Otherwise, use default.
            if faculty_password:
                if password == faculty_password:
                    # Set session for faculty
                    request.session['user_type'] = 'faculty'
                    request.session['faculty_id'] = faculty_id
                    # Optionally create a Django user for session auth
                    User = get_user_model()
                    user, created = User.objects.get_or_create(username=faculty_id)
                    if created:
                        user.set_unusable_password()
                        user.save()
                    user.backend = 'Login.auth_backend.FirestoreBackend'
                    login(request, user)
                    return redirect('home-page')
                else:
                    messages.error(request, "Incorrect password. Please enter your set password.")
                    return render(request, 'Login/faculty-login.html', {'error_field': 'password'})
            else:
                if password == "welcomeadmin":
                    request.session['user_type'] = 'faculty'
                    request.session['faculty_id'] = faculty_id
                    User = get_user_model()
                    user, created = User.objects.get_or_create(username=faculty_id)
                    if created:
                        user.set_unusable_password()
                        user.save()
                    user.backend = 'Login.auth_backend.FirestoreBackend'
                    login(request, user)
                    return redirect('home-page')
                else:
                    messages.error(request, "Incorrect password. Please enter the default password.")
                    return render(request, 'Login/faculty-login.html', {'error_field': 'password'})
        else:
            messages.error(request, "Faculty not authorized. Enter a different ID.")
            return render(request, 'Login/faculty-login.html', {'error_field': 'faculty_id'})

    return render(request, 'Login/faculty-login.html')

def Faculty_logout_view(request):
    """Logs out the faculty account and redirects to the login page."""
    if request.method == 'POST':  # Ensure logout is triggered via POST for security
        # Clear the session
        request.session.flush()
        messages.success(request, "You have been logged out successfully.")
        return redirect('faculty_login')  # Redirect to the faculty login page
    else:
        # If accessed via GET, redirect to the home page or login page
        return redirect('faculty_login')
    


def Superadmin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('Superadmin-homepage')  # or your superadmin homepage URL name
        else:
            messages.error(request, "Invalid credentials or not a superadmin.")
            return render(request, 'Login/superadmin-login.html')
    return render(request, 'Login/superadmin-login.html')



def superadmin_logout(request):
    if request.method == 'POST':  # Ensure logout is triggered via POST for security
        # Clear the session
        request.session.flush()
        messages.success(request, "You have been logged out successfully.")
        return redirect('superadmin_login')  # Redirect to the faculty login page
    else:
        # If accessed via GET, redirect to the home page or login page
        return redirect('superadmin_login')