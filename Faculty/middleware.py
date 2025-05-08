# Faculty/middleware.py

from django.shortcuts import redirect

def auth_required(get_response):
    def middleware(request):
        allowed_paths = ['/login/faculty/', '/reset-password/']

        if not request.session.get('is_authenticated') and request.path not in allowed_paths:
            return redirect('faculty_login')

        return get_response(request)
    return middleware
