from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Student
from Faculty.models import Faculty, FacultyAssignment
from firebase_admin import firestore
from .models import PendingStudent, Student
from django.http import JsonResponse
import json

# Firestore database instance
from SentinelsProject.firebase_config import db


def check_student_id(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id', '').strip()
            
            # Check if student ID exists in either PendingStudent or Student tables
            exists = (
                PendingStudent.objects.filter(student_id=student_id).exists() or 
                Student.objects.filter(student_id=student_id).exists()
            )
            
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def StudentRegister(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        middle_initial = request.POST.get("middle_initial", "").strip()
        program = request.POST.get("program", "").strip()
        year_section = request.POST.get("year_section", "").strip()
        semester = request.POST.get("semester", "").strip()

        # Server-side validation and formatting
        try:
            # Format names (proper case)
            import re
            first_name = ' '.join(word.capitalize() for word in re.sub(r'[^a-zA-Z\s]', '', first_name).split())
            last_name = ' '.join(word.capitalize() for word in re.sub(r'[^a-zA-Z\s]', '', last_name).split())
            
            # Format middle initial (single letter + period)
            middle_initial = middle_initial.upper()
            if len(middle_initial) > 0 and middle_initial[0].isalpha():
                middle_initial = middle_initial[0] + '.'
            else:
                messages.error(request, "Middle initial must be a single letter.")
                return redirect('student_register')
            
            # Format year_section (digit + letter, uppercase)
            year_section = year_section.upper()
            if not re.match(r'^[1-4][A-Z]$', year_section):
                messages.error(request, "Year and Section must be a number (1-4) followed by a capital letter.")
                return redirect('student_register')
            
            # Additional validation
            if not first_name or not last_name:
                messages.error(request, "First name and last name are required.")
                return redirect('student_register')
            
            faculty_assignment = FacultyAssignment.objects.filter(
                program=program,
                year_section=year_section,
                semester=semester,
                is_active=True,
                faculty__faculty_status='Continuing'
            ).first()
            
            if not faculty_assignment:
                messages.error(request, "Registration failed: No active class found for the selected program, year, and semester.")
                return redirect('student_register')

            # Check if student is already pending or registered
            if PendingStudent.objects.filter(student_id=student_id).exists() or Student.objects.filter(student_id=student_id).exists():
                 messages.error(request, f"Student ID '{student_id}' is already registered or pending approval.")
                 return redirect('student_register')

            # Create a new PendingStudent instance with formatted data
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
            return redirect("register_success")

        except Exception as e:
            messages.error(request, f"An error occurred during registration: {e}")
            return redirect('student_register')

    # For GET request, just render the form 
    return render(request, 'StudentRegistration/student-registration.html')

def RegisterSuccess(request):
    return render(request, 'StudentRegistration/register-success.html')