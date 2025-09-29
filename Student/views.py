from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Student
from Faculty.models import Faculty
from firebase_admin import firestore
from .models import PendingStudent, Student

# Firestore database instance
from SentinelsProject.firebase_config import db


def StudentRegister(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        middle_initial = request.POST.get("middle_initial")
        program = request.POST.get("program")
        year_section = request.POST.get("year_section")
        semester = request.POST.get("semester")

        try:
            # Check if a faculty for this class exists and is active
            if not Faculty.objects.filter(
                program=program,
                year_section=year_section,
                semester=semester,
                faculty_status='Continuing'
            ).exists():
                messages.error(request, "Registration failed: No active class found for the selected program, year, and semester.")
                return redirect('student_register')

            # Check if student is already pending or registered
            if PendingStudent.objects.filter(student_id=student_id).exists() or Student.objects.filter(student_id=student_id).exists():
                 messages.error(request, f"Student ID '{student_id}' is already registered or pending approval.")
                 return redirect('student_register')

            # Create a new PendingStudent instance
            PendingStudent.objects.create(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                middle_initial=middle_initial,
                program=program,
                year_section=year_section,
                semester=semester,
                password=make_password(student_id), # Using student_id as default password
            )

            messages.success(request, "Registration submitted successfully! Please wait for faculty approval.")
            return redirect("register_success") # Or redirect to login page

        except Exception as e:
            messages.error(request, f"An error occurred during registration: {e}")
            return redirect('student_register')

    # For GET request, just render the form
    return render(request, 'StudentRegistration/student-registration.html')

def RegisterSuccess(request):
    return render(request, 'StudentRegistration/register-success.html')