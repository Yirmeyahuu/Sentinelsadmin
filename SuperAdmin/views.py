from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from django.http import JsonResponse
from django.templatetags.static import static
from Login.decorators import superadmin_required
from .forms import ActivityDeadlineForm






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

    context = {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "tier_labels": tiers,
        "cs_tier_data": tier_counts["Computer Science"],
        "it_tier_data": tier_counts["Information Technology"],
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Home/contents/superadmin-home-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Home/superadmin-home.html', context)

@superadmin_required
def Faculty_list(request):
    # Fetch all continuing faculty
    continuing_ref = db.collection("Authorized Faculty")
    continuing_docs = continuing_ref.stream()
    continuing_faculties = [{**doc.to_dict(), 'status': 'Continuing'} for doc in continuing_docs]

    # Fetch all deactivated faculty
    deactivated_ref = db.collection("Deactivated Faculty")
    deactivated_docs = deactivated_ref.stream()
    deactivated_faculties = [{**doc.to_dict(), 'status': 'Deactivated'} for doc in deactivated_docs]

    # Fetch all completed faculty
    completed_ref = db.collection("Completed Faculty")
    completed_docs = completed_ref.stream()
    completed_faculties = [{**doc.to_dict(), 'status': 'Completed'} for doc in completed_docs]

    # Combine all
    faculties = continuing_faculties + deactivated_faculties + completed_faculties

    context = {
        "faculties": faculties
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Faculty/contents/faculty-list-content.html', context)
    else:
        return render(request, 'Faculty/faculty-list.html', context)

def add_faculty(request):

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
    
    archive_ref = db.collection("Archived Faculty")
    docs = archive_ref.stream()

    archived_faculties = [doc.to_dict() for doc in docs]

    context = {
        "archived_faculties": archived_faculties
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Faculty/contents/faculty-archived-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Faculty/faculty-archived.html', context)


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

    context = {"activities_novice": activities_novice,
                   "activities_junior": activities_junior,
                   "activities_senior": activities_senior,
                   "faculty_data": faculty_data,
                    "notifications": notifications,
                    "deadline_form": deadline_form,
                    "show_sticky_container": False,
                }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Activities/contents/activities-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Activities/activities.html', context)

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

    context = {
        "students": all_students,
        "section_label": f"{program} - {year_section}",
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Faculty/contents/student-status-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Faculty/student-status.html', context)

@superadmin_required
def Faculty_status(request):
    # Fetch all continuing faculty
    continuing_ref = db.collection("Authorized Faculty")
    continuing_docs = continuing_ref.stream()
    continuing_faculties = [{**doc.to_dict(), 'status': 'Continuing'} for doc in continuing_docs]

    # Fetch all deactivated faculty
    deactivated_ref = db.collection("Deactivated Faculty")
    deactivated_docs = deactivated_ref.stream()
    deactivated_faculties = [{**doc.to_dict(), 'status': 'Deactivated'} for doc in deactivated_docs]

    # Fetch all completed faculty
    completed_ref = db.collection("Completed Faculty")
    completed_docs = completed_ref.stream()
    completed_faculties = [{**doc.to_dict(), 'status': 'Completed'} for doc in completed_docs]

    # Combine all
    all_faculties = continuing_faculties + deactivated_faculties + completed_faculties

    context = {
        "faculties": all_faculties
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Faculty/contents/faculty-status-content.html', context)
    else:
        return render(request, 'Faculty/faculty-status.html', context)
    
@superadmin_required
def move_faculty(request):
    if request.method == "POST":
        faculty_id = request.POST.get("faculty_id")
        destination = request.POST.get("destination")

        # Find the faculty in any of the three collections
        collections = ["Authorized Faculty", "Deactivated Faculty", "Completed Faculty"]
        faculty_data = None
        source_collection = None
        for collection in collections:
            ref = db.collection(collection).document(faculty_id)
            doc = ref.get()
            if doc.exists:
                faculty_data = doc.to_dict()
                source_collection = collection
                break

        if not faculty_data:
            messages.error(request, "Faculty not found.")
            return redirect("FacultyList")

        # Remove from source collection (except if moving to archive)
        if destination != "archive" and source_collection:
            db.collection(source_collection).document(faculty_id).delete()

        # Move to the selected collection and update status
        if destination == "authorized":
            faculty_data["status"] = "Continuing"
            db.collection("Authorized Faculty").document(faculty_id).set(faculty_data)
            messages.success(request, "Faculty moved to Authorized Faculty successfully.")
        elif destination == "completed":
            faculty_data["status"] = "Completed"
            db.collection("Completed Faculty").document(faculty_id).set(faculty_data)
            messages.success(request, "Faculty moved to Completed Faculty successfully.")
        elif destination == "deactivated":
            faculty_data["status"] = "Deactivated"
            db.collection("Deactivated Faculty").document(faculty_id).set(faculty_data)
            messages.success(request, "Faculty moved to Deactivated Faculty successfully!")
        elif destination == "archive":
            db.collection("Archived Faculty").document(faculty_id).set(faculty_data)
            # Remove from all other collections
            if source_collection:
                db.collection(source_collection).document(faculty_id).delete()
            messages.success(request, "Faculty moved to Archived Faculty successfully!")
        else:
            messages.error(request, "Invalid destination.")
            return redirect("FacultyList")
    return redirect("FacultyList")

@superadmin_required
def student_list(request):
    # Get filter parameters
    selected_program = request.GET.get('program', 'all')
    selected_year_section = request.GET.get('year_section', 'all')
    selected_semester = request.GET.get('semester', 'all')
    
    # Base query
    students_ref = db.collection("Registered_Students")
    
    # Apply filters
    if selected_program != 'all':
        students_ref = students_ref.where("program", "==", selected_program)
    
    # Get all students before additional filtering
    students = [doc.to_dict() for doc in students_ref.stream()]
    
    # Apply additional filters in Python (since Firestore can't do multiple where clauses with different fields)
    if selected_year_section != 'all':
        students = [s for s in students if s.get('year_section') == selected_year_section]
    
    if selected_semester != 'all':
        students = [s for s in students if s.get('semester') == selected_semester]
    
    # Get unique year sections for the filter dropdown
    year_sections = sorted(list(set(s.get('year_section') for s in students if s.get('year_section'))))
    
    # Count statistics
    total_students = len(students)
    cs_count = len([s for s in students if s.get('program') == 'Computer Science'])
    it_count = len([s for s in students if s.get('program') == 'Information Technology'])
    inactive_count = len([s for s in students if s.get('status') == 'Drop-out'])
    
    context = {
        'students': students,
        'total_students': total_students,
        'cs_count': cs_count,
        'it_count': it_count,
        'inactive_count': inactive_count,
        'selected_program': selected_program,
        'selected_year_section': selected_year_section,
        'selected_semester': selected_semester,
        'year_sections': year_sections,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/student-list-content.html', context)
    else:
        return render(request, 'Students/student-list.html', context)