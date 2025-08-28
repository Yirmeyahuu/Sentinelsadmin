from django.shortcuts import redirect
from django.urls import reverse

def auth_required(get_response):
    def middleware(request):
        allowed_paths = ['/login/faculty/', '/reset-password/', '/change-password/', '/logout/']

        # Check if user is authenticated
        if not request.session.get('user_type') == 'faculty' and request.path not in allowed_paths:
            return redirect('sentinels_login')

        # Check if user needs to change password
        if (request.session.get('requires_password_change') and 
            request.path not in [reverse('change_password'), reverse('faculty_logout')]):
            return redirect('change_password')

        return get_response(request)
    return middleware