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
    # Redirect authenticated users to their respective homepages
    if request.user.is_authenticated:
        user_type = request.session.get('user_type')
        if user_type == 'superadmin':
            return redirect('Superadmin-homepage')
        elif user_type == 'faculty':
            return redirect('home-page')

    if request.method == 'POST':
        username_or_id = request.POST.get('username_or_id')
        password = request.POST.get('password')

        user = authenticate(request, username=username_or_id, password=password)
        if user is not None:
            # Check if superadmin
            if user.is_superuser:
                login(request, user)
                request.session['user_type'] = 'superadmin'
                return redirect('Superadmin-homepage')
            else:
                # Faculty authenticated via HybridFacultyBackend
                login(request, user)
                request.session['user_type'] = 'faculty'
                request.session['faculty_id'] = username_or_id

                # Optionally, redirect to password change page if needed
                # (You can add a flag in your Faculty model or session if you want this logic)
                # Example:
                # if not user.profile.password_updated:
                #     return redirect('change_password')

                return redirect('home-page')

        # If login fails for any reason, show a generic error
        return render(request, 'Login/sentinels-login.html', {
            'general_error': 'Invalid credentials. Please try again.',
            'entered_username': username_or_id
        })

    return render(request, 'Login/sentinels-login.html')


def Faculty_logout_view(request):
    """Logs out the faculty account and redirects to the login page."""
    if request.method == 'POST':  # Ensure logout is triggered via POST for security
        logout(request)  # Django logout
        request.session.flush()  # Extra safety: clear session data
        messages.success(request, "You have been logged out successfully.")
        return redirect('sentinels_login')
    else:
        # If accessed via GET, redirect to the login page
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
    
def change_password_view(request):
    """Allows faculty to change their password after first login."""
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        faculty_id = request.session.get('faculty_id')

        if faculty_id and new_password:
            # Update Firestore with the new password
            doc_ref = db.collection('Authorized Faculty').document(faculty_id)
            doc_ref.update({
                'faculty_password': new_password,
                'password_updated': True
            })

            messages.success(request, "Password updated successfully. Successfully Login.")
            
            return redirect('home-page')

    return render(request, 'Login/change-password.html')