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
    if request.headers.get('HX-Request'):
        # Handle the request as an HTMX request
        return render(request, 'Home/faculty-home.html')
    faculty_id = request.user.username

    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()

    faculty_data = None
    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    return render(request, 'Home/faculty-home.html', {"faculty_data": faculty_data})

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


