from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
from Faculty.models import Faculty

# Firestore database instance
from SentinelsProject.firebase_config import db



def Sentinels_login_view(request):
    # Redirect authenticated users to their respective homepages
    if request.user.is_authenticated:
        user_type = request.session.get('user_type')
        if user_type == 'superadmin':
            messages.success(request, "You have successfully logged in.")
            return redirect('Superadmin-homepage')
        elif user_type == 'faculty':
            messages.success(request, "You have successfully logged in.")
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
        confirm_password = request.POST.get('confirm_password')
        faculty_id = request.session.get('faculty_id')

        if not faculty_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('sentinels_login')

        # Basic validation
        if not new_password or not confirm_password:
            messages.error(request, "Both password fields are required.")
            return render(request, 'Login/change-password.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'Login/change-password.html')

        # Only check if password is not the default
        if new_password == "welcomeadmin":
            messages.error(request, "Please choose a different password than the default.")
            return render(request, 'Login/change-password.html')

        # Optional: Minimum length check (you can remove this too if you want complete freedom)
        if len(new_password) < 3:
            messages.error(request, "Password must be at least 3 characters long.")
            return render(request, 'Login/change-password.html')

        try:
            # Update PostgreSQL with the new password
            faculty = Faculty.objects.get(faculty_id=faculty_id)
            faculty.set_password(new_password)
            faculty.password_changed = True
            faculty.password_changed_at = timezone.now()
            faculty.save()

            # Clear the password change requirement from session
            request.session['requires_password_change'] = False

            messages.success(request, "Password updated successfully!")
            return redirect('home-page')

        except Faculty.DoesNotExist:
            messages.error(request, "Faculty profile not found.")
            return redirect('sentinels_login')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'Login/change-password.html')

    return render(request, 'Login/change-password.html')