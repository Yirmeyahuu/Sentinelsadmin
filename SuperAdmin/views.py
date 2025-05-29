from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from django.http import JsonResponse
from django.templatetags.static import static
from Login.decorators import superadmin_required





# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/Users/ASUS/Desktop/Super_Admin/sentinels-repository/sentinels-a61ff-firebase-adminsdk-fbsvc-35c84e60a7.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


@superadmin_required
def Superadmin_Home(request):
    db = firestore.client()

    # Total students
    students_ref = db.collection("Registered_Students")
    students = students_ref.stream()
    total_students = sum(1 for _ in students)

    # Total faculty
    faculty_ref = db.collection("Authorized Faculty")
    faculty = faculty_ref.stream()
    total_faculty = sum(1 for _ in faculty)

    # Computer Science students
    cs_students_ref = db.collection("Registered_Students").where("program", "==", "Computer Science")
    cs_students = cs_students_ref.stream()
    cs_students_count = sum(1 for _ in cs_students)

    # Information Technology students
    it_students_ref = db.collection("Registered_Students").where("program", "==", "Information Technology")
    it_students = it_students_ref.stream()
    it_students_count = sum(1 for _ in it_students)

    tiers = ["Novice", "Junior", "Senior"]
    programs = ["Computer Science", "Information Technology"]
    tier_counts = {prog: [] for prog in programs}

    for prog in programs:
        for tier in tiers:
            count = db.collection("Registered_Students") \
                .where("program", "==", prog) \
                .where("tier", "==", tier).stream()
            tier_counts[prog].append(sum(1 for _ in count))

    return render(request, 'Home/superadmin-home.html', {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "tier_labels": tiers,
        "cs_tier_data": tier_counts["Computer Science"],
        "it_tier_data": tier_counts["Information Technology"],
    })

@superadmin_required
def Faculty_list(request):
    """Fetch all active faculty members"""
    faculty_ref = db.collection("Authorized Faculty")
    docs = faculty_ref.stream()

    faculties = [doc.to_dict() for doc in docs]

    return render(request, "Faculty/faculty-list.html", {"faculties": faculties})

def add_faculty(request):
    """Add a new faculty member to Firestore"""
    if request.method == "POST":
        faculty_data = {
            "faculty_id": request.POST.get("faculty_id"),
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "middle_initial": request.POST.get("middle_initial"),
            "program": request.POST.get("program"),
            "year_section": request.POST.get("year_section"),
            "semester": request.POST.get("semester")
        }

        db.collection("Authorized Faculty").document(faculty_data["faculty_id"]).set(faculty_data)

        return JsonResponse({"success": True, "faculty_id": faculty_data["faculty_id"]})

    return JsonResponse({"success": False})

def edit_faculty(request, faculty_id):
    """Update faculty member details in Firestore"""
    faculty_ref = db.collection("Authorized Faculty").document(faculty_id)
    faculty = faculty_ref.get()

    if not faculty.exists:
        messages.error(request, "Faculty member not found.")
        return redirect("Superadmin-homepage")

    if request.method == "POST":
        updated_data = {
            "first_name": request.POST.get("first_name"),
            "last_name": request.POST.get("last_name"),
            "middle_initial": request.POST.get("middle_initial"),
            "program": request.POST.get("program"),
            "year_section": request.POST.get("year_section"),
            "semester": request.POST.get("semester")
        }
        faculty_ref.update(updated_data)

        messages.success(request, "Faculty details updated successfully!")
        return redirect("faculty-page")

    faculty_data = faculty.to_dict()
    return render(request, "Admin/EditFaculty.html", {"faculty": faculty_data})


def archive_faculty(request, faculty_id):
    """Move faculty member to 'archive' collection"""
    faculty_ref = db.collection("Authorized Faculty").document(faculty_id)
    faculty = faculty_ref.get()

    if faculty.exists:
        db.collection("Archived Faculty").document(faculty_id).set(faculty.to_dict())
        faculty_ref.delete()

        messages.success(request, "Faculty member has been archived successfully!")
    else:
        messages.error(request, "Faculty member not found.")

    return redirect("FacultyList")

@superadmin_required
def Archived_faculty_list(request):
    """Fetch all archived faculty members"""
    archive_ref = db.collection("Archived Faculty")
    docs = archive_ref.stream()

    archived_faculties = [doc.to_dict() for doc in docs]

    return render(request, "Faculty/faculty-archived.html", {"archived_faculties": archived_faculties})

def restore_faculty(request, faculty_id):
    """Restore faculty member from 'archive' collection"""
    archive_ref = db.collection("Archived Faculty").document(faculty_id)
    faculty = archive_ref.get()

    if faculty.exists:
        db.collection("Authorized Faculty").document(faculty_id).set(faculty.to_dict())
        archive_ref.delete()

        messages.success(request, "Faculty member has been restored successfully!")
    else:
        messages.error(request, "Faculty member not found in archive.")

    return redirect("archive-page")

@superadmin_required
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

    return render(request, "Activities/Superadmin_Activity_List.html",
                  {"activities_novice": activities_novice, "activities_junior": activities_junior, "activities_senior": activities_senior})

@superadmin_required
def student_status(request):
    # Set the section you want to display
    program = "Computer Science"
    year_section = "3A"

    # Fetch continuing students for this section
    continuing_ref = db.collection("Registered_Students")
    continuing_query = continuing_ref.where("program", "==", program).where("year_section", "==", year_section)
    continuing_students = [{**doc.to_dict(), 'status': 'continuing', 'id': doc.id} for doc in continuing_query.stream()]

    # Fetch dropout students for this section
    dropout_ref = db.collection("Drop-out Students")
    dropout_query = dropout_ref.where("program", "==", program).where("year_section", "==", year_section)
    dropout_students = [{**doc.to_dict(), 'status': 'dropout', 'id': doc.id} for doc in dropout_query.stream()]

    all_students = continuing_students + dropout_students

    return render(request, "Faculty/student-status.html", {
        "students": all_students,
        "section_label": f"{program} - {year_section}",
    })
