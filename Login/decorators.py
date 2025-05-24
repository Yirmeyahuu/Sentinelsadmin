from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render


def faculty_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.session.get('user_type') == 'faculty':
            return view_func(request, *args, **kwargs)
        elif request.user.is_authenticated:
            # Logged in but not faculty
            return render(request, 'Login/permission_denied.html')
        return redirect('sentinels_login')
    return _wrapped_view

def superadmin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        elif request.user.is_authenticated:
            # Logged in but not superadmin
            return render(request, 'Login/permission_denied.html')
        return redirect('sentinels_login')
    return _wrapped_view