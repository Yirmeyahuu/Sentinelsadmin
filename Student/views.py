from django.shortcuts import render, redirect
from firebase_admin import firestore, initialize_app
from django.contrib import messages

# Firestore database instance
db = firestore.client()

def StudentRegister(request):
    if request.method== "POST":
        student_data = {
            "student_id": request.POST.get("student_id"),
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "middle_initial": request.POST.get("middle_initial"),
            "program": request.POST.get("program"),
            "year_section": request.POST.get("year_section"),
            "semester": request.POST.get("semester")
        }

        db.collection("Student Verification").document(student_data["student_id"]).set(student_data)
        messages.success(request, "Student member added successfully!")
        return redirect("register_success")  # Redirect to the success page

    return render(request, 'StudentRegistration/student-registration.html')

def RegisterSuccess(request):
    return render(request, 'StudentRegistration/register-success.html')