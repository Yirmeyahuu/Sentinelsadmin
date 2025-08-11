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
from .forms import ActivityDeadlineForm, AddStudentForm
from django.views.decorators.csrf import csrf_exempt
from Login.decorators import faculty_required
from django.core.paginator import Paginator

from Faculty.models import Faculty




# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("/Users/jeremiahpantaras/Documents/sentinels-project/sentinels-a61ff-firebase-adminsdk-fbsvc-aaf9572a3f.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()



@csrf_exempt
@faculty_required
def saveActivityDeadline(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            faculty_id = request.user.username
            title = data.get('title')
            tier = data.get('tier')
            date = data.get('date')
            time = data.get('time')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

        db.collection('Activity Deadlines').document(faculty_id).set({
            title: {
                'tier': tier,
                'title': title,
                'deadline_date': date,
                'deadline_time': time,
                'created_at': firestore.SERVER_TIMESTAMP
            }
        }, merge=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@faculty_required
def Faculty_home(request):
    faculty_id = request.user.username

    # Get faculty data from PostgreSQL
    try:
        faculty_obj = Faculty.objects.get(faculty_id=faculty_id)
        faculty_data = {
            "faculty_id": faculty_obj.faculty_id,
            "first_name": faculty_obj.first_name,
            "last_name": faculty_obj.last_name,
            "middle_initial": faculty_obj.middle_initial,
            "program": faculty_obj.program,
            "year_section": faculty_obj.year_section,
            "semester": faculty_obj.semester,
        }
    except Faculty.DoesNotExist:
        faculty_data = None

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
    deadlines_doc = db.collection('Activity Deadlines').document(faculty_id).get()
    activity_deadlines = {}
    almost_due_tasks = []

    from datetime import datetime, timedelta
    current_date = datetime.now()

    if deadlines_doc.exists:
        deadlines_data = deadlines_doc.to_dict()
        for key, deadline_data in deadlines_data.items():
            deadline_date = datetime.strptime(deadline_data['deadline_date'], '%Y-%m-%d')
            day = deadline_date.day
            activity_deadlines[day] = {
                'title': deadline_data['title'],
                'tier': deadline_data.get('tier', ''),
                'description': deadline_data.get('description', ''),
                'date_of_deadline': deadline_data['deadline_date'],
                'time_of_deadline': deadline_data['deadline_time'],
            }
            # Almost Due: within next 7 days
            if current_date <= deadline_date <= (current_date + timedelta(days=7)):
                color = 'red' if deadline_date <= (current_date + timedelta(days=2)) else \
                       'yellow' if deadline_date <= (current_date + timedelta(days=4)) else 'green'
                almost_due_tasks.append({
                    'name': f"{deadline_data['tier']}: {deadline_data['title']}",
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
                    deadline = activity_deadlines[day]
                    day_data.update({
                        'deadline_title': deadline['title'],
                        'deadline_tier': deadline['tier'],
                        'deadline_description': deadline.get('description', ''),
                        'deadline_date': deadline['date_of_deadline'],
                        'deadline_time': deadline['time_of_deadline'],
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

    # --- Novice Task Progress for Chart ---
    novice_task_keys = [
        "Novice_Task_1(Collect Books)",
        "Novice_Task_2(Collect USB)",
        "Novice_Task_3(QNA)",
        "Novice_Task_4_(Defeat Rootkit)",
    ]

    junior_task_keys = [
        "Junior_Task_1(Collect Evidence)",
        "Junior_Task_2(Decrypt USB)",
        "Junior_Task_3(QNA)",
        "Junior_Task_4_(Defeat Rootkit)",
    ]
    senior_task_keys = [
        "Senior_Task_1(Scan Network)",
        "Senior_Task_2(Analyze Traffic)",
        "Senior_Task_3(QNA)",
        "Senior_Task_4_(Defeat Rootkit)",
    ]
    novice_task_counts = [0, 0, 0, 0]
    junior_task_counts = [0, 0, 0, 0]
    senior_task_counts = [0, 0, 0, 0]
    if faculty_data:
        faculty_program = faculty_data.get('program')
        faculty_year_section = faculty_data.get('year_section')
        faculty_semester = faculty_data.get('semester')

        students_query = db.collection("Registered_Students") \
            .where("program", "==", faculty_program) \
            .where("year_section", "==", faculty_year_section) \
            .where("semester", "==", faculty_semester) \
            .stream()

        for doc in students_query:
            student = doc.to_dict()
            for idx, task_key in enumerate(novice_task_keys):
                if isinstance(student.get(task_key), dict) and student.get(task_key):
                    novice_task_counts[idx] += 1
            for idx, task_key in enumerate(junior_task_keys):
                if isinstance(student.get(task_key), dict) and student.get(task_key):
                    junior_task_counts[idx] += 1
            for idx, task_key in enumerate(senior_task_keys):
                if isinstance(student.get(task_key), dict) and student.get(task_key):
                    senior_task_counts[idx] += 1

    # --- Leaderboard Logic ---
    leaderboard_students = []
    if faculty_data:
        faculty_program = faculty_data.get('program')
        faculty_year_section = faculty_data.get('year_section')
        faculty_semester = faculty_data.get('semester')

        students_query = db.collection("Registered_Students") \
            .where("program", "==", faculty_program) \
            .where("year_section", "==", faculty_year_section) \
            .where("semester", "==", faculty_semester) \
            .stream()

        task_keys = novice_task_keys

        for doc in students_query:
            student = doc.to_dict()
            total_points = 0
            for task_key in task_keys:
                task = student.get(task_key)
                if task and isinstance(task, dict):
                    total_points += int(task.get("points", 0))
            if total_points > 0:
                leaderboard_students.append({
                    "name": f"{student.get('first_name', '')} {student.get('last_name', '')}",
                    "points": total_points,
                })

        leaderboard_students = sorted(leaderboard_students, key=lambda x: x["points"], reverse=True)[:10]

    context = {
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
        "novice_task_counts": novice_task_counts,
        "junior_task_counts": junior_task_counts,
        "senior_task_counts": senior_task_counts,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Home/contents/faculty-home-content.html', context)
    else:
        return render(request, 'Home/faculty-home.html', context)


@csrf_exempt
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
    # Fetch faculty data
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
    
    # Get faculty's assigned program, year_section, and semester
    faculty_program = faculty_data.get('program')
    faculty_year_section = faculty_data.get('year_section')
    faculty_semester = faculty_data.get('semester')

    # 1. All students in the program
    program_total = db.collection("Registered_Students").where("program", "==", faculty_program).stream()
    program_total = sum(1 for _ in program_total)

    # 2. Students in program, year_section, semester
    section_query = db.collection("Registered_Students") \
        .where("program", "==", faculty_program) \
        .where("year_section", "==", faculty_year_section) \
        .where("semester", "==", faculty_semester)
    section_total = sum(1 for _ in section_query.stream())

    # 3 & 4. Active/Inactive students in that group
    active_count = 0
    inactive_count = 0
    for doc in section_query.stream():
        data = doc.to_dict()
        if data.get("is_active"):
            active_count += 1
        else:
            inactive_count += 1

    student_ref = db.collection("Registered_Students")
    filters = []
    if faculty_program:
        filters.append(("program", "==", faculty_program))
    if faculty_year_section:
        filters.append(("year_section", "==", faculty_year_section))

    docs_query = student_ref
    for field, op, value in filters:
        docs_query = docs_query.where(field, op, value)
    docs = docs_query.stream()
    students = [{**doc.to_dict(), "student_id": doc.id} for doc in docs]

    # --- Server-side search ---
    search_query = request.GET.get('search', '').strip().lower()
    if search_query:
        students = [
            s for s in students
            if search_query in str(s.get('first_name', '')).lower()
            or search_query in str(s.get('last_name', '')).lower()
            or search_query in str(s.get('student_id', '')).lower()
        ]

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(students, 8)  # 12 students per page
    page_obj = paginator.get_page(page_number)


    # Fetch notifications from Firestore, newest first
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    context ={
        "students": page_obj.object_list,
        "faculty_data": faculty_data,
        "total_users": total_users,
        "notifications": notifications,
        "program_total": program_total,
        "section_total": section_total,
        "active_count": active_count,
        "inactive_count": inactive_count,
        "search_query": request.GET.get('search', ''),
        "show_sticky_container": False,
        "page_obj": page_obj,
        "paginator": paginator,
        "request": request, 
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Students/contents/student-list-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Students/student-list.html', context)


@faculty_required
def student_progress(request):
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None
    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()

    faculty_program = faculty_data.get('program')
    faculty_year_section = faculty_data.get('year_section')
    faculty_semester = faculty_data.get('semester')

    program_total = db.collection("Registered_Students").where("program", "==", faculty_program).stream()
    program_total = sum(1 for _ in program_total)

    section_query = db.collection("Registered_Students") \
        .where("program", "==", faculty_program) \
        .where("year_section", "==", faculty_year_section) \
        .where("semester", "==", faculty_semester)

    section_total = sum(1 for _ in section_query.stream())

    # Count students who accomplished each tier
    novice_count = 0
    junior_count = 0
    senior_count = 0


    task_keys = [
        "Novice_Task_1(Collect Books)",
        "Novice_Task_2(Collect USB)",
        "Novice_Task_3(QNA)",
        "Novice_Task_4_(Defeat Rootkit)",
    ]
    for doc in section_query.stream():
        data = doc.to_dict()
        if all(isinstance(data.get(task), dict) and data.get(task) for task in task_keys):
            novice_count += 1

    active_count = 0
    inactive_count = 0
    for doc in section_query.stream():
        data = doc.to_dict()
        if data.get("is_active"):
            active_count += 1
        else:
            inactive_count += 1

    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)

    context = {
        "faculty_data": faculty_data,
        "notifications": notifications,
        "program_total": program_total,
        "section_total": section_total,
        "active_count": active_count,
        "inactive_count": inactive_count,
        "novice_count": novice_count,
        "junior_count": junior_count,
        "senior_count": senior_count,
        "show_sticky_container": False,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/students-progress-content.html', context)
    else:
        return render(request, 'Students/students-progress.html', context)



@faculty_required
def add_student(request):
    if request.method == "POST":
        form = AddStudentForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data["student_id"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            middle_initial = form.cleaned_data["middle_initial"]

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
            semester = faculty_data.get("semester")

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
            return redirect("faculty-student-list")
        else:
            context = {
                "form": form,
                "show_add_modal": True,
            }
            return render(request, "Students/contents/student-list-content.html", context)
    return redirect("faculty-student-list")


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

@faculty_required
def archived_students_list_page(request):
    archived_students = [
        {**doc.to_dict(), "student_id": doc.id}
        for doc in db.collection("Archived Students").stream()
    ]
    context = {
        "archived_students": archived_students,
        "search_query": request.GET.get('search', ''),
    }
    # Only render content for HTMX requests, otherwise render full page
    if request.headers.get('HX-Request'):
        return render(request, "Students/contents/students-archived-content.html", context)
    else:
        return render(request, "Students/students-archived.html", context)

def restore_student(request, student_id, destination="registered"):
    archive_ref = db.collection("Archived Students").document(student_id)
    student = archive_ref.get()

    if student.exists:
        student_data = student.to_dict()
        if destination == "registered":
            student_data["status"] = "Continuing"
            db.collection("Registered_Students").document(student_id).set(student_data)
        elif destination == "completed":
            student_data["status"] = "Completed"
            db.collection("Completed Students").document(student_id).set(student_data)
        elif destination == "dropout":
            student_data["status"] = "Drop-out"
            db.collection("Drop-out Students").document(student_id).set(student_data)
        archive_ref.delete()
        messages.success(request, "Student has been restored successfully!")
    else:
        messages.error(request, "Student not found in archive.")

    return redirect("archived_students_list")

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

    # --- Server-side search ---
    search_query = request.GET.get('search', '').strip().lower()
    if search_query:
        verify_students = [
            s for s in verify_students
            if search_query in str(s.get('first_name', '')).lower()
            or search_query in str(s.get('last_name', '')).lower()
            or search_query in str(s.get('student_id', '')).lower()
        ]

    context = {
        "verify_students": verify_students,
        "faculty_data": faculty_data,
        "notifications": notifications,
        "search_query": request.GET.get('search', ''),
        "show_sticky_container": False,
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Students/contents/students-verify-list-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Students/students-verify-list.html', context)



#This is the activity page for the faculty
def Faculty_activity_page(request):
    faculty_id = request.user.username

    # Get faculty data
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = None
    if query:
        faculty_doc = query[0]
        faculty_data = faculty_doc.to_dict()


    activities_novice = [
        {
            "title": "Novice Task 1",
            "description": "In this quest, the player begins their journey at CyberTech Academy, guided by their instructor, Katrina Salazar, who assigns their first task: researching the meaning of cybersecurity. As the player explores the library, a memory of their late father—a legendary cybersecurity expert—resurfaces, emphasizing the importance of understanding the people behind the systems. The quest unfolds through interactive NPC encounters, where the player answers questions to define cybersecurity, identify key career paths such as Security Architect and Ethical Hacker, and understand the anatomy of a cyber attack. Each correct response unlocks achievements and advances the story, immersing the player in a hands-on introduction to the world of cybersecurity.",
            "image": static("assets/img/Photo1.png"),
        },
        {
            "title": "Novice Task 2",
            "description": "In this second quest, the player continues their training at CyberTech Academy, diving deeper into the realities of cybersecurity threats and vulnerabilities. A vivid flashback recalls a stormy night when the player's father swiftly neutralized a cyber threat, warning that the key to defense lies in identifying weak spots before attackers do. Now seated in the computer lab, the player begins researching risks that organizations face. Through a sequence of NPC-guided tasks, they must correctly identify internal threats like employees, recognize cybersecurity vulnerabilities such as card skimmers, and demonstrate understanding of core principles like the CIA Triad—particularly how confidentiality relies on encryption and hashing. Each correct answer grants achievements and brings the player closer to mastering the fundamentals of digital defense.",
            "image": static("assets/img/Photo2.png"),
        },
        {
            "title": "Novice Task 3",
            "description": "In the third and final quest, the player is challenged to apply their growing knowledge of cybersecurity to real-world frameworks and strategies. A flashback to a simple but powerful lesson from their father—*People, Processes, Technology*—sets the stage for what lies ahead. Tasked with interviewing the right faculty members, the player must navigate the faculty office, identifying which professors hold the expertise needed to discuss security tactics, emerging technologies, and types of cybersecurity. Choosing the wrong person leads to rejection, while finding the right expert unlocks valuable insights. Returning to the classroom, the player answers reflection questions based on their interviews. With each correct response and interaction, achievements are earned, bringing them one step closer to becoming a well-rounded digital defender, just like their father envisioned.",
            "image": static("assets/img/Photo3.png"),
        },
        {
            "title": "Novice Boss Battle",
            "description": "In the Novice Boss Battle, the player faces their first major test as the academy's network is suddenly compromised. The school's AI assistant has been hijacked and transformed into *The Deceiver AI*, a malicious entity designed to challenge the player’s grasp of cybersecurity. As classroom screens fade to black and a chilling robotic voice taunts them, the player recalls their father’s warning about social engineering: that deception, not just intrusion, is a hacker’s greatest weapon. To stop the AI from spreading misinformation and damaging the academy's defenses, the player must correctly answer three tricky cybersecurity questions that blur the line between truth and lie. Success earns them the **“Defender of Knowledge”** achievement, while failure results in data corruption and a forced retry—proving that in cybersecurity, knowing the truth is the first line of defense.",
            "image": static("assets/img/Photo4.png"),
        },
    ]

    activities_junior = [
        {
            "title": "Junior Task 1",
            "description": "In Task 1, the player starts their internship in a cybersecurity office and is assigned to research the concept of a domain. A flashback with their father emphasizes the importance of organized systems in network security. The player uses their workstation to investigate and is later questioned by the CISO. If they correctly define a domain as a group of devices managed under the same rules, they are allowed to proceed. A wrong answer sends them back to research before moving to the **Incident Response Room** to study cryptography.",
            "image": static("assets/img/Photo1.png"),
        },
        {
            "title": "Junior Task 2",
            "description": "In Task 2, the player enters the Incident Response Room to assist an employee named John with a suspicious encrypted email. A flashback from their father highlights the dual nature of encryption—protective but potentially dangerous. After analyzing the email using basic cipher clues, the player must choose the correct response: report the email and isolate the system. A correct choice earns praise and leads to a report to the CISO. The task ends with the player writing a policy to help others recognize phishing attempts.",
            "image": static("assets/img/Photo2.png"),
        },
        {
            "title": "Junior Task 3",
            "description": "In Task 3, the player drafts a company security policy, reminded by their father that people are the strongest defense against cyber threats. They must choose the best policy to protect the company. The correct choice is to train employees to recognize and report phishing emails. Selecting this earns praise for promoting awareness. Wrong answers prompt a reminder that effective policies focus on education, not restrictions or risky behavior.",
            "image": static("assets/img/Photo3.png"),
        },
        {
            "title": "Junior Boss Battle",
            "description": "In the Junior Boss Battle, the player faces a crafty hacker disguised as an employee who uses social engineering tactics to steal data. The player must spot fake emails, false boss impersonations, and phishing login pages before time expires. Falling for any trick means restarting the fight. Success rewards the “Master of Awareness” achievement. A flashback reminds the player that the biggest threats often come disguised as harmless.",
            "image": static("assets/img/Photo4.png"),
        },
    ]

    activities_senior = [
        {
            "title": "Senior Task 1",
            "description": "Threat Landscape, the player is called to the Cyber Threat Intelligence Lab to analyze the company’s network for vulnerabilities. Guided by a flashback of their father’s advice, they must identify weak points before attackers do. The key challenge is recognizing that weak passwords on wireless access points are a major risk. Correct answers lead to praise and progression; wrong answers require retrying the analysis. This task emphasizes the importance of spotting real network threats early.",
            "image": static("assets/img/Photo1.png"),
        },
        {
            "title": "Senior Task 2",
            "description": "Ontology of Malware, the player analyzes a malware report on the Malware Analysis Workstation to classify a new threat. Guided by a flashback from their father, they learn that malware can be deceptive as well as destructive. The player must identify ransomware—a type that encrypts files and demands payment—based on its behavior. Correct identification earns praise and progression; mistakes require retrying the classification. This task highlights the importance of recognizing malware types for effective cybersecurity responses.",
            "image": static("assets/img/Photo2.png"),
        },
        {
            "title": "Senior Task 3",
            "description": "Risk Management & Incident Countermeasure, the player leads a simulated breach response after an alert shows unauthorized access and data theft. A flashback reminds them that quick action is crucial during an attack. The player must choose the best first steps—disconnecting the compromised system and blocking the attacker’s IP—to contain the threat. Correct choices earn praise and progress, while wrong ones prompt a retry. This task emphasizes swift and effective incident response in cybersecurity.",
            "image": static("assets/img/Photo3.png"),
        },
        {
            "title": "Senior Boss Battle",
            "description": "The player now faces an advanced AI-powered malware that adapts to every defense they deploy. The virus launches attacks like DDoS, ransomware, and privilege escalation, and the player must quickly select the correct countermeasure to stop each one. Acting too slowly or choosing wrong lets the virus mutate, making it harder to defeat. Success earns the “Cyber Guardian” achievement. A flashback reminds the player: threats evolve fast, so staying sharp and acting swiftly is key.",
            "image": static("assets/img/Photo4.png"),
        },
    ]

        # Fetch lock states from Game Triggers
    
    game_triggers_ref = db.collection("Game Triggers")
    doc_map = {
        'Novice': 'Novice State',
        'Junior': 'Junior State',
        'Senior': 'Senior State'
    }
    lock_states = {}
    for tier, doc_name in doc_map.items():
        doc = game_triggers_ref.document(doc_name).get()
        if doc.exists:
            lock_states[tier] = doc.to_dict().get(f"{tier} isLock", True)  # Default to locked
        else:
            lock_states[tier] = True
    
    # Get activity deadlines from Firestore
    deadlines_doc = db.collection('Activity Deadlines').document(faculty_id).get()
    activity_deadlines = {}
    if deadlines_doc.exists:
        deadlines_data = deadlines_doc.to_dict()
        for key, deadline_data in deadlines_data.items():
            activity_deadlines[deadline_data['title']] = deadline_data['deadline_date']
    
    # Add isLock and deadline_date to each activity
    for activity in activities_novice:
        activity['isLock'] = lock_states['Novice']
        activity['deadline_date'] = activity_deadlines.get(activity['title'])
    for activity in activities_junior:
        activity['isLock'] = lock_states['Junior']
        activity['deadline_date'] = activity_deadlines.get(activity['title'])
    for activity in activities_senior:
        activity['isLock'] = lock_states['Senior']
        activity['deadline_date'] = activity_deadlines.get(activity['title'])

    context = {
        "faculty_data": faculty_data,
        "activities_novice": activities_novice,
        "activities_junior": activities_junior,
        "activities_senior": activities_senior,
        "show_sticky_container": False,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Activities/contents/Faculty-Activity-List-content.html', context)
    else:
        return render(request, 'Activities/Faculty-Activity-List.html', context)


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
    try:
        faculty_obj = Faculty.objects.get(faculty_id=faculty_id)
        faculty_data = {
            "faculty_id": faculty_obj.faculty_id,
            "first_name": faculty_obj.first_name,
            "last_name": faculty_obj.last_name,
            "middle_initial": faculty_obj.middle_initial,
            "program": faculty_obj.program,
            "year_section": faculty_obj.year_section,
            "semester": faculty_obj.semester,
            "profile_image": getattr(faculty_obj, "profile_image", None),  # If you have this field
        }
    except Faculty.DoesNotExist:
        faculty_data = None

    show_logout_modal = False

    context = {
        'faculty_data': faculty_data,
        'show_logout_modal': show_logout_modal,
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Faculty/contents/faculty-account-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Faculty/faculty-account.html', context)
    
@faculty_required
def edit_faculty_account(request):
    faculty_id = request.user.username
    # Query for the document where faculty_id matches in Firestore
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_ref = query[0].reference if query else None

    if request.method == "POST" and faculty_ref:
        updates = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_initial': request.POST.get('middle_initial'),
        }
        try:
            # Update PostgreSQL
            Faculty.objects.filter(faculty_id=faculty_id).update(
                first_name=updates['first_name'],
                last_name=updates['last_name'],
                middle_initial=updates['middle_initial']
            )
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, 'Failed to update profile. Please try again.')
            print(f"Error updating profile: {e}")

    return redirect("faculty-account")

def handle_image_upload(image):
    # Implement your image upload logic
    pass

@faculty_required
def move_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        destination = request.POST.get("destination")

        collections = [
            "Registered_Students",
            "Completed Students",
            "Drop-out Students",
            "Archived Students"
        ]
        student = None
        student_data = None
        found_collection = None

        for collection in collections:
            ref = db.collection(collection).document(student_id)
            doc = ref.get()
            if doc.exists:
                student = ref
                student_data = doc.to_dict()
                found_collection = collection
                break

        if not student_data:
            messages.error(request, "Student not found.")
            return redirect("faculty-student-list")

        if destination == "registered":
            # Set status to Continuing, move to Registered_Students
            student_data["status"] = "Continuing"
            db.collection("Registered_Students").document(student_id).set(student_data)
            # Remove from old collection if not already there
            if found_collection != "Registered_Students":
                student.delete()
            messages.success(request, "Student set as Continuing in Registered Students.")
        elif destination == "completed":
            student_data["status"] = "Completed"
            db.collection("Completed Students").document(student_id).set(student_data)
            if found_collection != "Completed Students":
                student.delete()
            messages.info(request, "Student moved to Completed Students successfully.")
        elif destination == "dropout":
            student_data["status"] = "Drop-out"
            db.collection("Drop-out Students").document(student_id).set(student_data)
            if found_collection != "Drop-out Students":
                student.delete()
            messages.success(request, "Student moved to Drop-out Students successfully!")
        elif destination == "archive":
            student_data["status"] = "Archived"
            db.collection("Archived Students").document(student_id).set(student_data)
            if found_collection != "Archived Students":
                student.delete()
            messages.success(request, "Student moved to Archived Students successfully!")
        else:
            messages.error(request, "Invalid destination.")
            return redirect("faculty-student-list")
    return redirect(request.META.get('HTTP_REFERER', 'faculty-student-list'))

@faculty_required
def novice_tier(request):
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = query[0].to_dict() if query else {}

    faculty_program = faculty_data.get('program')
    faculty_year_section = faculty_data.get('year_section')
    faculty_semester = faculty_data.get('semester')

    # Task map for filtering
    task_map = {
        "task1": "Novice_Task_1(Collect Books)",
        "task2": "Novice_Task_2(Collect USB)",
        "task3": "Novice_Task_3(QNA)",
        "task4": "Novice_Task_4_(Defeat Rootkit)",
    }
    selected_task = request.GET.get("task", "task1")
    selected_task_map = task_map.get(selected_task, "Novice_Task_1(Collect Books)")

    students_query = db.collection("Registered_Students") \
        .where("program", "==", faculty_program) \
        .where("year_section", "==", faculty_year_section) \
        .where("semester", "==", faculty_semester) \
        .stream()

    novice_students = []
    leaderboard_students = []

    for doc in students_query:
        student = doc.to_dict()
        # For progress table (filtered by selected task)
        task_data = student.get(selected_task_map)
        if task_data:
            novice_students.append({
                "student_id": student.get("student_id", doc.id),
                "first_name": student.get("first_name", ""),
                "last_name": student.get("last_name", ""),
                "points": task_data.get("points", 0),
                "total_time_completed": task_data.get("time_taken", ""),
            })
        # For leaderboard (sum all tasks)
        total_points = 0
        for task_key in task_map.values():
            task = student.get(task_key)
            if task and isinstance(task, dict):
                total_points += int(task.get("points", 0))
        if total_points > 0:
            leaderboard_students.append({
                "student_id": student.get("student_id", doc.id),
                "first_name": student.get("first_name", ""),
                "last_name": student.get("last_name", ""),
                "points": total_points,
            })

    # Sort leaderboard by total points descending``
    novice_leaderboard = sorted(
        leaderboard_students,
        key=lambda x: x["points"],
        reverse=True
    )

    context = {
        "novice_students": novice_students,
        "novice_leaderboard": novice_leaderboard,
        "faculty_data": faculty_data,
        "selected_task": selected_task,
    }
    return render(request, 'Tier/Novice.html', context)

@faculty_required
def junior_tier(request):
    return render(request, 'Tier/Junior.html')

@faculty_required
def senior_tier(request):
    return render(request, 'Tier/Senior.html')



@faculty_required
def faculty_student_status(request):
    faculty_id = request.user.username
    users_ref = db.collection('Authorized Faculty')
    query = users_ref.where('faculty_id', '==', faculty_id).limit(1).get()
    faculty_data = query[0].to_dict() if query else None

    # Get faculty's assigned program, year_section, semester
    faculty_program = faculty_data.get('program')
    faculty_year_section = faculty_data.get('year_section')
    faculty_semester = faculty_data.get('semester')

    search_query = request.GET.get('search', '').strip().lower()
    status_filter = request.GET.get('status', 'all').lower()

    # Fetch Completed Students
    completed_ref = db.collection("Completed Students")
    completed_query = (
        completed_ref
        .where("program", "==", faculty_program)
        .where("year_section", "==", faculty_year_section)
        .where("semester", "==", faculty_semester)
    )
    completed_students = [{**doc.to_dict(), "student_id": doc.id, "status": "Completed"} for doc in completed_query.stream()]

    # Fetch Drop-out Students
    dropout_ref = db.collection("Drop-out Students")
    dropout_query = (
        dropout_ref
        .where("program", "==", faculty_program)
        .where("year_section", "==", faculty_year_section)
        .where("semester", "==", faculty_semester)
    )
    dropout_students = [{**doc.to_dict(), "student_id": doc.id, "status": "Drop-out"} for doc in dropout_query.stream()]

    # Combine and filter by status if needed
    students = completed_students + dropout_students
    if status_filter == "completed":
        students = [s for s in students if s["status"].lower() == "completed"]
    elif status_filter == "drop-out" or status_filter == "dropout":
        students = [s for s in students if s["status"].lower() in ["drop-out", "dropout"]]

    # Search
    if search_query:
        students = [
            s for s in students
            if search_query in str(s.get('first_name', '')).lower()
            or search_query in str(s.get('last_name', '')).lower()
            or search_query in str(s.get('student_id', '')).lower()
        ]

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(students, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        "students": page_obj.object_list,
        "faculty_data": faculty_data,
        "status_filter": status_filter,
        "search_query": request.GET.get('search', ''),
        "page_obj": page_obj,
        "paginator": paginator,
        "request": request,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/student-status-content.html', context)
    else:
        return render(request, 'Students/student-status.html', context)