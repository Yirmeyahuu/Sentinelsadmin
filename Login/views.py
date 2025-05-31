from django.contrib import messages  # Corrected import for messages
from django.shortcuts import render, redirect
from firebase_admin import credentials, firestore
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from Login.decorators import faculty_required, superadmin_required
from django.http import HttpResponseRedirect

db = firestore.client()
# Initialize Firebase Admin SDK

def Sentinels_login_view(request):
    # If already logged in as superadmin or faculty
    if request.user.is_authenticated and request.session.get('user_type') in ['superadmin', 'faculty']:
        # Try to redirect to previous page if available
        referer = request.META.get('HTTP_REFERER')
        if referer and not referer.endswith('/'):
            return HttpResponseRedirect(referer)
        # Fallback to homepage
        if request.session.get('user_type') == 'superadmin':
            return redirect('Superadmin-homepage')
        else:
            return redirect('home-page')
    
    if request.method == 'POST':
        username_or_id = request.POST.get('username_or_id')
        password = request.POST.get('password')

        # 1. Try Django superuser authentication (Superadmin)
        user = authenticate(request, username=username_or_id, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            request.session['user_type'] = 'superadmin'
            return redirect('Superadmin-homepage')

        # 2. Try Faculty authentication (Firestore)
        users_ref = db.collection('Authorized Faculty')
        query = users_ref.where('faculty_id', '==', username_or_id).limit(1).get()
        if query:
            faculty_doc = query[0]
            faculty_data = faculty_doc.to_dict()
            faculty_password = faculty_data.get('faculty_password')
            if (faculty_password and password == faculty_password) or (not faculty_password and password == "welcomeadmin"):
                request.session['user_type'] = 'faculty'
                request.session['faculty_id'] = username_or_id
                User = get_user_model()
                user, created = User.objects.get_or_create(username=username_or_id)
                if created:
                    user.set_unusable_password()
                    user.save()
                user.backend = 'Login.auth_backend.FirestoreBackend'
                login(request, user)
                return redirect('home-page')
            else:
                messages.error(request, "Incorrect password.")
                return render(request, 'Login/sentinels-login.html', {'error_field': 'password'})
        else:
            messages.error(request, "User not found or not authorized.")
            return render(request, 'Login/sentinels-login.html', {'error_field': 'username_or_id'})

    return render(request, 'Login/sentinels-login.html')

def Faculty_logout_view(request):
    """Logs out the faculty account and redirects to the login page."""
    if request.method == 'POST':  # Ensure logout is triggered via POST for security
        # Clear the session
        request.session.flush()
        messages.success(request, "You have been logged out successfully.")
        return redirect('sentinels_login')  # Redirect to the faculty login page
    else:
        # If accessed via GET, redirect to the home page or login page
        return redirect('sentinels_login')


def superadmin_logout(request):
    if request.method == 'POST':  # Ensure logout is triggered via POST for security
        # Clear the session
        request.session.flush()
        messages.success(request, "You have been logged out successfully.")
        return redirect('sentinels_login')  # Redirect to the faculty login page
    else:
        # If accessed via GET, redirect to the home page or login page
        return redirect('sentinels_login')