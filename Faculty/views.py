from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.templatetags.static import static
from django.views.decorators.http import require_POST



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

    # Fetch notifications from Firestore, newest first
    
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)
        unseen_count = sum(1 for notif in notifications if notif.get('seen', False))


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
        "notifications": notifications,  # Pass notifications to template
        "unseen_count": unseen_count,  # Pass unseen count to template
    })

@login_required(login_url='faculty_login')
def student_list(request):
    # Add this block to fetch faculty_data
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None
    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    # Get ALL students for total count (no filters)
    all_students_ref = db.collection("Registered_Students")
    all_students_docs = all_students_ref.stream()
    total_users = sum(1 for _ in all_students_docs)
    
    # Now apply filters for the table
    program_filter = request.GET.get('program')
    year_section_filter = request.GET.get('year_section')
    semester_filter = request.GET.get('semester')

    student_ref = db.collection("Registered_Students")
    filters = []
    if program_filter and program_filter != "all":
        filters.append(("program", "==", program_filter))
    if year_section_filter and year_section_filter != "all":
        filters.append(("year_section", "==", year_section_filter))
    if semester_filter and semester_filter != "all":
        filters.append(("semester", "==", semester_filter))

    docs_query = student_ref
    for field, op, value in filters:
        docs_query = docs_query.where(field, op, value)
    docs = docs_query.stream()
    students = [{**doc.to_dict(), "student_id": doc.id} for doc in docs]

    # Define your dropdown options
    year_section_options = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"]
    semester_options = ["1st Semester", "2nd Semester"]

    # Fetch notifications from Firestore, newest first
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    return render(request, "Students/student-list.html", {
        "students": students,
        "faculty_data": faculty_data,  # Now faculty_data is defined
        "selected_program": program_filter or "all",
        "selected_year_section": year_section_filter or "all",
        "selected_semester": semester_filter or "all",
        "year_section_options": year_section_options,
        "semester_options": semester_options,
        "total_users": total_users,
        "notifications": notifications, 
    })


def student_dashboard (request):
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None
    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    # Fetch notifications from Firestore, newest first
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    return render(request, 'Students/students-dashboard.html', {
        "faculty_data": faculty_data,
        "notifications": notifications,  # Pass notifications to template
    })  # Corrected context name



@login_required(login_url='faculty_login')
def add_student(request):
    if request.method == "POST":
        # Get form data and add to Firestore
        student_id = request.POST.get("student_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        middle_initial = request.POST.get("middle_initial")
        program = request.POST.get("program")
        year_section = request.POST.get("year_section")
        semester = request.POST.get("semester")

        db.collection("Registered_Students").document(student_id).set({
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "middle_initial": middle_initial,
            "program": program,
            "year_section": year_section,
            "semester": semester,
        })
        # Optionally add a Django message here
        messages.success(request, f"Student {student_id} added successfully!")
        return redirect("student-list")
    return redirect("student-list")


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
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None
    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    """Fetch all archived student members"""
    archive_ref = db.collection("Archived Students")
    docs = archive_ref.stream()

    # Fetch notifications from Firestore, newest first
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    archived_students = [
        {**doc.to_dict(), "student_id": doc.id} for doc in docs
    ]  # Ensuring student_id is included

    return render(request, "Students/students-archived.html", {
    "archived_students": archived_students,
    "faculty_data": faculty_data,
    "notifications": notifications,  # Pass notifications to template
    })  # Corrected context name

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

@login_required(login_url='faculty_login')
def Verify_Student(request):
    """Verify student member"""
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None

    # Fetch notifications from Firestore, newest first
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    verify_ref = db.collection("Pending Students")  # <-- Correct collection
    docs = verify_ref.stream()

    verify_students = [{**doc.to_dict(), "student_id": doc.id} for doc in docs]

    return render(request, "Students/students-verify-list.html", {
        "verify_students": verify_students,
        "faculty_data": faculty_data,
        "notifications": notifications,  # Pass notifications to template
    })




#This is the activity page for the faculty
def activity_page(request):
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None

    # Fetch notifications from Firestore, newest first
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

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
                  {"activities_novice": activities_novice,
                   "activities_junior": activities_junior,
                   "activities_senior": activities_senior,
                   "faculty_data": faculty_data,
                    "notifications": notifications,  # Pass notifications to template
                   })  # Corrected context name


@login_required(login_url='faculty_login')
def accept_student(request, student_id):
    """Accept student and move to Registered_Students collection"""
    pending_ref = db.collection("Pending Students").document(student_id)
    student = pending_ref.get()

    if student.exists:
        # Move to Registered_Students
        db.collection("Registered_Students").document(student_id).set(student.to_dict())
        # Delete from Pending Students
        pending_ref.delete()
        
        # Add success notification
        notification = {
            "message": f"Student {student.to_dict()['first_name']} {student.to_dict()['last_name']} has been accepted and registered.",
            "timestamp": firestore.SERVER_TIMESTAMP,
            "seen": False
        }
        db.collection("Notifications").add(notification)
        
        messages.success(request, "Student has been accepted and registered successfully!")
    else:
        messages.error(request, "Student not found in pending list.")

    return redirect("verify-students")

@login_required(login_url='faculty_login')
def reject_student(request, student_id):
    """Reject and remove student from Pending Students"""
    pending_ref = db.collection("Pending Students").document(student_id)
    student = pending_ref.get()

    if student.exists:
        # Get student info before deletion for notification
        student_data = student.to_dict()
        # Delete from Pending Students
        pending_ref.delete()
        
        # Add rejection notification
        notification = {
            "message": f"Student {student_data['first_name']} {student_data['last_name']}'s registration was rejected.",
            "timestamp": firestore.SERVER_TIMESTAMP,
            "seen": False
        }
        db.collection("Notifications").add(notification)
        
        messages.success(request, "Student registration has been rejected.")
    else:
        messages.error(request, "Student not found in pending list.")

    return redirect("verify-students")


@require_POST
@login_required(login_url='faculty_login')
def mark_all_notifications_read(request):
    notifications_ref = db.collection("Notifications")
    for notif in notifications_ref.stream():
        notif.reference.update({"seen": True})
    messages.success(request, "All notifications marked as read.")
    return redirect(request.META.get('HTTP_REFERER', '/'))