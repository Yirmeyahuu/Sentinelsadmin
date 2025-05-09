from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static


# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("/Users/jeremiahpantaras/Documents/sentinels-project/sentinels-a61ff-firebase-adminsdk-fbsvc-aaf9572a3f.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@login_required(login_url='faculty_login')
def Faculty_home(request):
    faculty_id = request.user.username

    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()

    faculty_data = None
    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    # Count total users from Registered_Students collection
    students_ref = db.collection("Registered_Students")
    students = students_ref.stream()
    total_users = sum(1 for _ in students)

    # Placeholder values for now
    active_percentage = 50
    inactive_percentage = 25

    calendar_days = [
        {'date': 29, 'today': False},
        {'date': 30, 'today': False},
        {'date': 31, 'today': False},
        {'date': 1, 'today': False},
        {'date': 2, 'today': False},
        {'date': 3, 'today': False},
        {'date': 4, 'today': False},
        {'date': 5, 'today': False},
        {'date': 6, 'today': False},
        {'date': 7, 'today': False},
        {'date': 8, 'today': False},
        {'date': 9, 'today': False},
        {'date': 10, 'today': False},
        {'date': 11, 'today': False},
        {'date': 12, 'today': False},
        {'date': 13, 'today': False},
        {'date': 14, 'today': False},
        {'date': 15, 'today': False},
        {'date': 16, 'today': False},
        {'date': 17, 'today': False},
        {'date': 18, 'today': False},
        {'date': 19, 'today': False},
        {'date': 20, 'today': True},
        {'date': 21, 'today': False},
        {'date': 22, 'today': False},
        {'date': 23, 'today': False},
        {'date': 24, 'today': False},
        {'date': 25, 'today': False},
        {'date': 26, 'today': False},
        {'date': 27, 'today': False},
        {'date': 28, 'today': True},
    ]

    almost_due_tasks = [
        {'name': 'Activity 1: Novice', 'color': 'red'},
        {'name': 'Activity 2: Novice', 'color': 'yellow'},
        {'name': 'Project 1: Novice', 'color': 'green'}
    ]

    return render(request, 'Home/faculty-home.html', {
        "faculty_data": faculty_data,
        "total_users": total_users,
        "active_percentage": active_percentage,
        "inactive_percentage": inactive_percentage,
        "calendar_days": calendar_days,
        "almost_due_tasks": almost_due_tasks,
    })

@login_required(login_url='faculty_login')
def student_list(request):
    """Fetch all active student members"""
    student_ref = db.collection("Registered_Students")
    docs = student_ref.stream()

    students = [{**doc.to_dict(), "student_id": doc.id} for doc in docs]  # Ensure student_id is included

    return render(request, "Students/student-list.html", {"students": students})  # Corrected context name

def student_dashboard (request):
    return render(request, 'Students/students-dashboard.html')



def add_student(request):
    """Add a new student member to Firestore"""
    if request.method == "POST":
        student_data = {
            "student_id": request.POST.get("student_id"),
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "middle_initial": request.POST.get("middle_initial"),
            "program": request.POST.get("program"),
            "year_section": request.POST.get("year_section"),
            "semester": request.POST.get("semester")
        }

        db.collection("Registered_Students").document(student_data["student_id"]).set(student_data)

        messages.success(request, "Student member added successfully!")
        return redirect("student-list")  # Redirect to the list

    return render(request, "Students/student-list.html")  # Render the form for adding a student


def edit_student(request, student_id):
    """Update student details in Firestore"""
    student_ref = db.collection("Registered_Students").document(student_id)  # Corrected collection name
    student = student_ref.get()

    if not student.exists:
        messages.error(request, "Student not found.")
        return redirect("student-list")

    if request.method == "POST":
        updated_data = {
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "middle_initial": request.POST.get("middle_initial"),
            "program": request.POST.get("program"),
            "year_section": request.POST.get("year_section"),
            "semester": request.POST.get("semester")
        }

        # Update Firestore document
        student_ref.update(updated_data)

        messages.success(request, "Student details updated successfully!")
        return redirect("student-list")

    student_data = student.to_dict()
    return render(request, "Admin/EditStudent.html", {"student": student_data})

def archive_student(request, student_id):
    """Move student member to 'archive' collection"""
    student_ref = db.collection("Registered_Students").document(student_id)
    student = student_ref.get()

    if student.exists:
        db.collection("Archived Students").document(student_id).set(student.to_dict())
        student_ref.delete()

        messages.success(request, "student member has been archived successfully!")
    else:
        messages.error(request, "student member not found.")

    return redirect("student-list")

def archived_student_list(request):
    """Fetch all archived student members"""
    archive_ref = db.collection("Archived Students")
    docs = archive_ref.stream()

    archived_students = [
        {**doc.to_dict(), "student_id": doc.id} for doc in docs
    ]  # Ensuring student_id is included

    return render(request, "Students/students-archived.html", {"archived_students": archived_students})  # Corrected context name

def restore_student(request, student_id):
    """Restore student member from 'archive' collection"""
    archive_ref = db.collection("Archived Students").document(student_id)
    student = archive_ref.get()

    if student.exists:
        db.collection("Registered_Students").document(student_id).set(student.to_dict())
        archive_ref.delete()

        messages.success(request, "student member has been restored successfully!")
    else:
        messages.error(request, "student member not found in archive.")

    return redirect("archive-page")

def Verify_Student(request):
    """Verify student member"""
    verify_ref = db.collection("Student Verification")
    docs = verify_ref.stream()

    verify_students = [{**doc.to_dict(), "student_id": doc.id} for doc in docs]  # Ensure student_id is included

    return render(request, "Students/students-verify-list.html", {"verify_students": verify_students})  # Corrected context name




#This is the activity page for the faculty
def activity_page(request):
    activities_novice = [
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,  # percentage
            "modules": 0,
            "image": static("assets/img/Photo1.png"),  # Update with your actual image path
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo2.png"),
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo3.png"),
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo4.png"),
        },
    ]

    activities_junior = [
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,  # percentage
            "modules": 0,
            "image": static("assets/img/Photo2.png"),  # Update with your actual image path
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo3.png"),
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo4.png"),
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo1.png"),
        },
    ]

    activities_senior = [
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,  # percentage
            "modules": 0,
            "image": static("assets/img/Photo3.png"),  # Update with your actual image path
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo4.png"),
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo1.png"),
        },
        {
            "title": "",
            "subject": "",
            "date": "",
            "progress": 0,
            "modules": 0,
            "image": static("assets/img/Photo2.png"),
        },
    ]

    return render(request, "Activities/activities.html",
                  {"activities_novice": activities_novice, "activities_junior": activities_junior, "activities_senior": activities_senior})


