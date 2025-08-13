from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Student
from Faculty.models import Faculty
from firebase_admin import firestore

# Firestore database instance (for notifications)
db = firestore.client()

def StudentRegister(request):
    if request.method == "POST":
        # Get data from the registration form
        student_id = request.POST.get("student_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        middle_initial = request.POST.get("middle_initial")
        program = request.POST.get("program")
        year_section = request.POST.get("year_section")
        semester = request.POST.get("semester")

        try:
            # Find the corresponding faculty member
            faculty = Faculty.objects.get(
                program=program,
                year_section=year_section,
                semester=semester,
                faculty_status='Continuing'  # Ensure faculty is active
            )

            # Create a new Student instance
            new_student = Student(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                middle_initial=middle_initial,
                # IMPORTANT: Hash the password before saving.
                # Using student_id as a temporary default password.
                # You should add a password field to your form.
                password=make_password(student_id),
                faculty=faculty,
                student_status='Registered'  # Set default status
            )

            new_student.save()

            # --- Keep Firestore notification for the superadmin ---
            full_name = f"{first_name} {middle_initial} {last_name}".strip()
            notification = {
                "message": f"A new student, {full_name}, has registered under Faculty {faculty.faculty_id}.",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "seen": False
            }
            db.collection("Notifications").add(notification)
            # ------------------------------------------------

            messages.success(request, "You have registered successfully!")
            return redirect("register_success")

        except Faculty.DoesNotExist:
            # Handle case where no matching faculty is found
            messages.error(request, "Registration failed: No active class found for the selected program, year, and semester.")
            return redirect('student_register') # Redirect back to the form
        except Exception as e:
            # Handle other potential errors, like a duplicate student ID
            messages.error(request, f"An error occurred: {e}")
            return redirect('student_register') # Redirect back to the form

    return render(request, 'StudentRegistration/student-registration.html')

def RegisterSuccess(request):
    return render(request, 'StudentRegistration/register-success.html')