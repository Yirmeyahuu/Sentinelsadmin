from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from django.contrib import messages
from django.templatetags.static import static
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.http import JsonResponse
import json
from .forms import ActivityDeadlineForm
from django.views.decorators.csrf import csrf_exempt
from Login.decorators import faculty_required, superadmin_required




# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("/Users/jeremiahpantaras/Documents/sentinels-project/sentinels-a61ff-firebase-adminsdk-fbsvc-aaf9572a3f.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()



def saveActivityDeadline(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            activity_id = data.get('activity_id')
            title = data.get('title')
            date = data.get('date')
            time = data.get('time')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

        db.collection('Activity Deadlines').add({
            'activity_id': activity_id,
            'title': title,
            'deadline_date': date,
            'deadline_time': time,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@faculty_required
def Faculty_home(request):
    faculty_id = request.user.username

    # Get faculty data
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None
    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    # Count total users
    students_ref = db.collection("Registered_Students")
    students = students_ref.stream()
    total_users = sum(1 for _ in students)

    # Count Computer Science students
    cs_students_ref = db.collection("Registered_Students").where("program", "==", "Computer Science")
    cs_students = cs_students_ref.stream()
    cs_count = sum(1 for _ in cs_students)

    # Count Information Technology students
    it_students_ref = db.collection("Registered_Students").where("program", "==", "Information Technology")
    it_students = it_students_ref.stream()
    it_count = sum(1 for _ in it_students)

    # Fetch notifications
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)
    unseen_count = sum(1 for notif in notifications if not notif.get('seen', False))

    # Get activity deadlines from Firestore
    deadlines_ref = db.collection('Activity Deadlines').stream()
    activity_deadlines = {}
    almost_due_tasks = []
    
    from datetime import datetime, timedelta
    current_date = datetime.now()
    
    for deadline in deadlines_ref:
        deadline_data = deadline.to_dict()
        deadline_date = datetime.strptime(deadline_data['date_of_deadline'], '%Y-%m-%d')
        day = deadline_date.day
        activity_deadlines[day] = {
            'title': deadline_data['title'],
            'description': deadline_data.get('description', ''),
            'date_of_deadline': deadline_data['date_of_deadline'],
            'time_of_deadline': deadline_data['time_of_deadline'],
        }
        
        # Check if deadline is within next 7 days for "Almost Due" section
        if current_date <= deadline_date <= (current_date + timedelta(days=7)):
            color = 'red' if deadline_date <= (current_date + timedelta(days=2)) else \
                   'yellow' if deadline_date <= (current_date + timedelta(days=4)) else 'green'
            
            almost_due_tasks.append({
                'name': deadline_data['title'],
                'color': color,
                'deadline': deadline_date.strftime('%Y-%m-%d')
            })

    # Sort almost due tasks by deadline
    almost_due_tasks.sort(key=lambda x: x['deadline'])

    # Calendar days with deadline information
    import calendar
    current_year = current_date.year
    current_month = current_date.month
    
    cal = calendar.monthcalendar(current_year, current_month)
    calendar_days = []
    for week in cal:
        for day in week:
            if day != 0:
                day_data = {
                    'date': day,
                    'today': day == current_date.day,
                    'has_deadline': day in activity_deadlines,
                }
                if day in activity_deadlines:
                    day_data.update({
                        'deadline_title': activity_deadlines[day]['title'],
                        'deadline_description': activity_deadlines[day].get('description', ''),
                        'deadline_date': activity_deadlines[day]['date_of_deadline'],
                        'deadline_time': activity_deadlines[day]['time_of_deadline'],
                    })
                calendar_days.append(day_data)

    # --- Quick Students Table Logic ---
    quick_students = []
    if faculty_data:
        faculty_program = faculty_data.get('program')
        faculty_year_section = faculty_data.get('year_section')
        if faculty_program and faculty_year_section:
            students_ref = db.collection("Registered_Students")
            students_query = (
                students_ref
                .where("program", "==", faculty_program)
                .where("year_section", "==", faculty_year_section)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(3)
            )
            quick_students = [doc.to_dict() for doc in students_query.stream()]

    # --- Quick Pending Students Table Logic ---
    quick_pending_students = []
    if faculty_data:
        faculty_program = faculty_data.get('program')
        faculty_year_section = faculty_data.get('year_section')
        if faculty_program and faculty_year_section:
            pending_ref = db.collection("Pending Students")
            pending_query = (
                pending_ref
                .where("program", "==", faculty_program)
                .where("year_section", "==", faculty_year_section)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(3)
            )
            quick_pending_students = [doc.to_dict() for doc in pending_query.stream()]

    leaderboard_students = [
    {'name': 'Alice Cruz', 'points': 120},
    {'name': 'Bob Reyes', 'points': 110},
    ]

    return render(request, 'Home/faculty-home.html', {
        "faculty_data": faculty_data,
        "total_users": total_users,
        "cs_count": cs_count,
        "it_count": it_count,
        "calendar_days": calendar_days,
        "almost_due_tasks": almost_due_tasks,
        "notifications": notifications,
        "unseen_count": unseen_count,
        "current_month": current_date.strftime('%B'),
        "current_year": current_year,
        "quick_students": quick_students,
        "quick_pending_students": quick_pending_students,
        "leaderboard_students": leaderboard_students,
    })


@csrf_exempt  # If you use POST and CSRF token in the form, you can remove this decorator
def remove_deadline(request):
    if request.method == "POST":
        title = request.POST.get('title')
        if title:
            from django.utils.text import slugify
            doc_name = slugify(title)
            db.collection('Activity Deadlines').document(doc_name).delete()
    return redirect('home-page')

@faculty_required
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
    
    # Get faculty's assigned program and year_section
    faculty_program = faculty_data.get('program')
    faculty_year_section = faculty_data.get('year_section')

    student_ref = db.collection("Registered_Students")
    filters = []
    if faculty_program:
        filters.append(("program", "==", faculty_program))
    if faculty_year_section:
        filters.append(("year_section", "==", faculty_year_section))

    # Optionally, allow further filtering by semester (if you want)
    semester_filter = request.GET.get('semester')
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
        "faculty_data": faculty_data,
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

    # Get assigned program and year_section
    faculty_program = faculty_data.get('program')
    faculty_year_section = faculty_data.get('year_section')

    # Count students in assigned program/year_section
    students_ref = db.collection("Registered_Students")
    students_query = students_ref.where("program", "==", faculty_program).where("year_section", "==", faculty_year_section)
    students = list(students_query.stream())
    total_students = len(students)

    # Count active and inactive users (assuming you have an 'is_active' field)
    active_students = [s for s in students if s.to_dict().get('is_active')]
    inactive_students = [s for s in students if not s.to_dict().get('is_active')]
    active_count = len(active_students)
    inactive_count = len(inactive_students)

    # Fetch notifications from Firestore, newest first
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    return render(request, 'Students/students-dashboard.html', {
        "faculty_data": faculty_data,
        "notifications": notifications,
        "total_students": total_students,
        "active_count": active_count,
        "inactive_count": inactive_count
    })



@faculty_required
def add_student(request):
    if request.method == "POST":
        # Get form data
        student_id = request.POST.get("student_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        middle_initial = request.POST.get("middle_initial")

        # Get faculty's assigned program, year_section, and semester
        faculty_id = request.user.username
        users_ref = db.collection('Authorized Faculty')
        query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
        faculty_data = None
        if query:
            faculty_doc = query[0]
            faculty_data = faculty_doc.to_dict()
        program = faculty_data.get("program")
        year_section = faculty_data.get("year_section")
        semester = faculty_data.get("semester")  # Make sure this exists in your faculty data

        db.collection("Registered_Students").document(student_id).set({
            "student_id": student_id,
            "first_name": first_name,
            "last_name": last_name,
            "middle_initial": middle_initial,
            "program": program,
            "year_section": year_section,
            "semester": semester,
            "created_at": firestore.SERVER_TIMESTAMP,
        })
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

@faculty_required
def Verify_Student(request):
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None

    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    # Get faculty's assigned program and year_section
    faculty_program = faculty_data.get('program')
    faculty_year_section = faculty_data.get('year_section')

    # Filter pending students by assigned program and year_section
    verify_ref = db.collection("Pending Students")
    filters = []
    if faculty_program:
        filters.append(("program", "==", faculty_program))
    if faculty_year_section:
        filters.append(("year_section", "==", faculty_year_section))

    docs_query = verify_ref
    for field, op, value in filters:
        docs_query = docs_query.where(field, op, value)
    docs = docs_query.stream()

    verify_students = [{**doc.to_dict(), "student_id": doc.id} for doc in docs]

    return render(request, "Students/students-verify-list.html", {
        "verify_students": verify_students,
        "faculty_data": faculty_data,
        "notifications": notifications,  
    })




#This is the activity page for the faculty
def activity_page(request):
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None
    deadline_form = ActivityDeadlineForm()


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
            "title": "Novice Task 1",
            "description": "Short description of the task 1.",
            "deadline": "",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo1.png"),
        },
        {
            "title": "Novice Task 2",
            "description": "Short description of the task 2.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo2.png"),
        },
        {
            "title": "Novice Task 3",
            "description": "Short description of the task 3.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo3.png"),
        },
        {
            "title": "Novice Boss Battle",
            "description": "Short description of the Boss Battle 1.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo4.png"),
        },
    ]

    activities_junior = [
        {
            "title": "Junior Task 1",
            "description": "Short description of the task 1.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo1.png"),
        },
        {
            "title": "Junior Task 2",
            "description": "Short description of the task 2.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo2.png"),
        },
        {
            "title": "Junior Task 3",
            "description": "Short description of the task 3.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo3.png"),
        },
        {
            "title": "Junior Boss Battle",
            "description": "Short description of the Boss Battle 2.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo4.png"),
        },
    ]

    activities_senior = [
        {
            "title": "Senior Task 1",
            "description": "Short description of the task 1.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo1.png"),
        },
        {
            "title": "Senior Task 2",
            "description": "Short description of the task 2.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo2.png"),
        },
        {
            "title": "Senior Task 3",
            "description": "Short description of the task 3.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo3.png"),
        },
        {
            "title": "Senior Boss Battle",
            "description": "Short description of the Boss Battle 3.",
            "deadline": "2023-10-15",
            "progress": 0,  # percentage
            "image": static("assets/img/Photo4.png"),
        },
    ]

    if request.method == "POST":
        deadline_form = ActivityDeadlineForm(request.POST)
        if deadline_form.is_valid():
            data = deadline_form.cleaned_data
            # Use the title as the document name (slugify for safety)
            from django.utils.text import slugify
            doc_name = slugify(data['title'])
            db.collection('Activity Deadlines').document(doc_name).set({
                'activity_id': data['activity_id'],
                'title': data['title'],
                'description': data['description'],
                'date_of_deadline': str(data['date']),
                'time_of_deadline': str(data['time']),
                'created_at': firestore.SERVER_TIMESTAMP
            })
            messages.success(request, "Deadline set successfully!")
            return redirect('activities-page')

    return render(request, "Activities/activities.html",
                  {"activities_novice": activities_novice,
                   "activities_junior": activities_junior,
                   "activities_senior": activities_senior,
                   "faculty_data": faculty_data,
                    "notifications": notifications,  # Pass notifications to template
                     "deadline_form": deadline_form,
                   })  # Corrected context name


@faculty_required
def accept_student(request, student_id):
    pending_ref = db.collection("Pending Students").document(student_id)
    student = pending_ref.get()
    if student.exists:
        student_data = student.to_dict()
        student_data["created_at"] = firestore.SERVER_TIMESTAMP  # <-- Add this line
        db.collection("Registered_Students").document(student_id).set(student_data)
        pending_ref.delete()
        
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

@faculty_required
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
@faculty_required
def mark_all_notifications_read(request):
    notifications_ref = db.collection("Notifications")
    for notif in notifications_ref.stream():
        notif.reference.update({"seen": True})
    messages.success(request, "All notifications marked as read.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@faculty_required
def faculty_account(request):
    faculty_id = request.user.username
    faculty_ref = db.collection('Authorized Faculty').document(faculty_id)
    faculty_doc = faculty_ref.get()
    faculty_data = faculty_doc.to_dict() if faculty_doc.exists else None

    show_logout_modal = False

    if request.method == "POST":
        updates = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_initial': request.POST.get('middle_initial'),
        }
        password_changed = False

        # Only allow password creation if not set yet
        if not faculty_data.get('faculty_password'):
            faculty_password = request.POST.get('faculty_password')
            if faculty_password:
                updates['faculty_password'] = faculty_password
                password_changed = True

        faculty_ref.update(updates)

        if password_changed:
            show_logout_modal = True  # Show modal instead of logging out immediately

    return render(request, 'Faculty/faculty-account.html', {
        'faculty_data': faculty_data,
        'show_logout_modal': show_logout_modal,
    })

def handle_image_upload(image):
    # Implement your image upload logic
    pass


@faculty_required
def move_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        destination = request.POST.get("destination")
        student_ref = db.collection("Registered_Students").document(student_id)
        student = student_ref.get()
        if not student.exists:
            messages.error(request, "Student not found.")
            return redirect("student-list")
        student_data = student.to_dict()
        # Move to the selected collection
        if destination == "completed":
            db.collection("Completed Students").document(student_id).set(student_data)
            messages.info(request, "Student moved to Completed Students successfully.")
        elif destination == "dropout":
            db.collection("Drop-out Students").document(student_id).set(student_data)
            student_ref.delete()
            messages.success(request, "Student moved to Drop-out Students successfully!")
        elif destination == "archive":
            db.collection("Archived Students").document(student_id).set(student_data)
            student_ref.delete()
            messages.success(request, "Student moved to Archived Students successfully!")
        else:
            messages.error(request, "Invalid destination.")
            return redirect("student-list")
    return redirect("student-list")