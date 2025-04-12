from django.shortcuts import render

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id')
        password = request.POST.get('faculty_password')

        # Look for the faculty document
        users_ref = db.collection('faculty')
        query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()

        if query:
            faculty_doc = query[0]
            faculty_data = faculty_doc.to_dict()

            if faculty_data['password'] == password:  # Just for now, assuming plain text
                # Successful login logic
                return redirect('student_dashboard')  # update this path
            else:
                messages.error(request, "Incorrect password.")
        else:
            messages.error(request, "Faculty ID not found.")

    return render(request, 'Login/login.html')

def superadmin_login_view(request):
    return render(request, 'Login/superadmin_login.html')