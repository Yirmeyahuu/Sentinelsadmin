from django.shortcuts import render, redirect, get_object_or_404
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
from Student.models import Student, PendingStudent, Task, StudentTaskProgress, ArchivedStudent
from django.db.models import Q

from django.db.models import Count, Sum, IntegerField
from django.db import transaction
from datetime import datetime, timedelta
import calendar
from django.db.models.functions import Cast




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
    # --- PostgreSQL Data Fetching ---
    try:
        faculty = Faculty.objects.get(faculty_id=request.user.username)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('some_error_page') # Or faculty login


    # Total students (PostgreSQL)
    total_students = Student.objects.filter(student_status='Registered').count()
    # Computer Science students (PostgreSQL)
    cs_students_count = Student.objects.filter(student_status='Registered', faculty__program='Computer Science').count()
    # Information Technology students (PostgreSQL)
    it_students_count = Student.objects.filter(student_status='Registered', faculty__program='Information Technology').count()

    # --- Quick Lists ---
    # Recently registered students in the faculty's section
    quick_students = Student.objects.filter(faculty=faculty).order_by('-pk')[:3]
    
    # Recently submitted pending students for the faculty's section
    quick_pending_students = PendingStudent.objects.filter(
        program=faculty.program,
        year_section=faculty.year_section,
        semester=faculty.semester
    ).order_by('-submitted_at')[:3]

    # --- Task Progress for Charts (from PostgreSQL) ---
    # Sync data first to ensure it's up-to-date
    sync_student_progress(faculty)

    # Now query the synced data
    task_progress = StudentTaskProgress.objects.filter(student__faculty=faculty)
    
    novice_task_counts = list(task_progress.filter(task__tier='Novice').values_list('task__description').annotate(c=Count('task_id')).values_list('c', flat=True))
    junior_task_counts = list(task_progress.filter(task__tier='Junior').values_list('task__description').annotate(c=Count('task_id')).values_list('c', flat=True))
    senior_task_counts = list(task_progress.filter(task__tier='Senior').values_list('task__description').annotate(c=Count('task_id')).values_list('c', flat=True))

    # --- Leaderboard Logic (from PostgreSQL) ---
    leaderboard_students = Student.objects.filter(
        faculty=faculty,
        progress_records__task__tier='Novice' # Base leaderboard on Novice tier points
    ).annotate(
        total_points=Sum(
            Cast('progress_records__details__points', output_field=IntegerField())
        )
    ).filter(total_points__gt=0).order_by('-total_points')[:10]


    # --- Firestore Logic (Notifications & Deadlines - Unchanged) ---
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)
    unseen_count = sum(1 for notif in notifications if not notif.get('seen', False))

    deadlines_doc = db.collection('Activity Deadlines').document(faculty.faculty_id).get()
    activity_deadlines = {}
    almost_due_tasks = []
    current_date = datetime.now()
    if deadlines_doc.exists:
        deadlines_data = deadlines_doc.to_dict()
        for key, deadline_data in deadlines_data.items():
            deadline_date = datetime.strptime(deadline_data['deadline_date'], '%Y-%m-%d')
            day = deadline_date.day
            activity_deadlines[day] = {
                'title': deadline_data['title'],
                'tier': deadline_data.get('tier', ''),
                'date_of_deadline': deadline_data['deadline_date'],
                'time_of_deadline': deadline_data['deadline_time'],
            }
            if current_date <= deadline_date <= (current_date + timedelta(days=7)):
                color = 'red' if deadline_date <= (current_date + timedelta(days=2)) else 'yellow' if deadline_date <= (current_date + timedelta(days=4)) else 'green'
                almost_due_tasks.append({
                    'name': f"{deadline_data['tier']}: {deadline_data['title']}",
                    'color': color,
                    'deadline': deadline_date.strftime('%Y-%m-%d')
                })
    almost_due_tasks.sort(key=lambda x: x['deadline'])

    cal = calendar.monthcalendar(current_date.year, current_date.month)
    calendar_days = []
    for week in cal:
        for day in week:
            if day != 0:
                day_data = {'date': day, 'today': day == current_date.day, 'has_deadline': day in activity_deadlines}
                if day in activity_deadlines:
                    day_data.update(activity_deadlines[day])
                calendar_days.append(day_data)
    # --- End of Firestore Logic ---

    context = {
        "faculty_data": faculty,
        "total_students": total_students,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "calendar_days": calendar_days,
        "almost_due_tasks": almost_due_tasks,
        "notifications": notifications,
        "unseen_count": unseen_count,
        "current_month": current_date.strftime('%B'),
        "current_year": current_date.year,
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


def sync_student_progress(faculty):
    """Helper function to sync Firestore progress to PostgreSQL for a given faculty."""
    tasks_by_tier = {}
    for task in Task.objects.all():
        tasks_by_tier.setdefault(task.tier, []).append(task)

    students_in_section = Student.objects.filter(faculty=faculty, student_status='Registered')

    for student in students_in_section:
        try:
            doc_ref = db.collection('Registered_Students').document(student.student_id).get()
            if not doc_ref.exists: continue
            progress_data = doc_ref.to_dict()

            for tier, tasks_in_tier in tasks_by_tier.items():
                required_keys = [t.firestore_key for t in tasks_in_tier]
                if all(key in progress_data for key in required_keys):
                    with transaction.atomic():
                        for task_to_sync in tasks_in_tier:
                            StudentTaskProgress.objects.get_or_create(
                                student=student,
                                task=task_to_sync,
                                defaults={'details': progress_data.get(task_to_sync.firestore_key, {})}
                            )
        except Exception as e:
            print(f"Error syncing progress for student {student.student_id}: {e}")


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
    # Get the logged-in faculty member from PostgreSQL
    try:
        faculty = Faculty.objects.get(faculty_id=request.user.username)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('some_error_page') # Or faculty login

    # Base query for students assigned to this faculty
    students_query = Student.objects.filter(faculty=faculty, student_status='Registered')

    # --- Server-side search ---
    search_query = request.GET.get('search', '').strip()
    if search_query:
        students_query = students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    students_query = students_query.order_by('last_name', 'first_name')

    # --- Calculate Counts from PostgreSQL ---
    # Total students in the faculty's specific class/section
    section_total = students_query.count()
    
    # Total students in the faculty's entire program
    program_total = Student.objects.filter(
        faculty__program=faculty.program, 
        student_status='Registered'
    ).count()

    # Total registered students in the system
    total_users = Student.objects.filter(student_status='Registered').count()

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(students_query, 8) # 8 students per page
    page_obj = paginator.get_page(page_number)

    # --- Notifications (still from Firestore as per existing logic) ---
    notifications_ref = db.collection("Notifications").order_by("timestamp", direction=firestore.Query.DESCENDING)
    notifications = []
    for doc in notifications_ref.stream():
        notif = doc.to_dict()
        notif['id'] = doc.id
        notifications.append(notif)
    # --- End of Firestore logic ---

    context = {
        "students": page_obj,
        "faculty_data": faculty,
        "total_users": total_users,
        "notifications": notifications,
        "program_total": program_total,
        "section_total": section_total,
        "search_query": search_query,
        "page_obj": page_obj,
        "paginator": paginator,
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Students/contents/student-list-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Students/student-list.html', context)


@faculty_required
def student_progress(request):
    try:
        faculty = Faculty.objects.get(faculty_id=request.user.username)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('some_error_page')

    # --- Sync Logic: Tier Completion Model ---

    # 1. Get all tasks from DB and group them by tier
    tasks_by_tier = {}
    all_tasks = Task.objects.all()
    for task in all_tasks:
        if task.tier not in tasks_by_tier:
            tasks_by_tier[task.tier] = []
        tasks_by_tier[task.tier].append(task)

    # 2. Get all students for this faculty
    students_in_section = Student.objects.filter(faculty=faculty, student_status='Registered')

    # 3. Iterate through students to check and sync progress
    for student in students_in_section:
        try:
            doc_ref = db.collection('Registered_Students').document(student.student_id).get()
            if not doc_ref.exists:
                continue  # Skip if student has no Firestore record

            progress_data = doc_ref.to_dict()

            # 4. Check each tier for completion
            for tier, tasks_in_tier in tasks_by_tier.items():
                # Get the required Firestore keys for this tier
                required_keys = [t.firestore_key for t in tasks_in_tier]
                
                # Check if ALL required keys are in the Firestore data
                if all(key in progress_data for key in required_keys):
                    
                    # Tier is complete in Firestore. Now, sync it to PostgreSQL.
                    with transaction.atomic(): # Ensure all tasks for the tier are saved together
                        for task_to_sync in tasks_in_tier:
                            # Use get_or_create to avoid creating duplicate entries
                            StudentTaskProgress.objects.get_or_create(
                                student=student,
                                task=task_to_sync,
                                defaults={'details': progress_data.get(task_to_sync.firestore_key, {})}
                            )

        except Exception as e:
            # It's good practice to log errors during the sync process
            print(f"Error syncing progress for student {student.student_id}: {e}")
    
    # --- End of Sync Logic ---

    # --- Final Counts from PostgreSQL ---
    # Now that data is synced, we can query PostgreSQL efficiently.
    # This counts students who have at least one progress record in a given tier.
    # Since we only add records upon full tier completion, this is accurate.
    
    novice_completed_count = Student.objects.filter(
        faculty=faculty, 
        progress_records__task__tier='Novice'
    ).distinct().count()

    junior_completed_count = Student.objects.filter(
        faculty=faculty, 
        progress_records__task__tier='Junior'
    ).distinct().count()

    senior_completed_count = Student.objects.filter(
        faculty=faculty, 
        progress_records__task__tier='Senior'
    ).distinct().count()

    context = {
        "faculty_data": faculty,
        "section_total": students_in_section.count(),
        "novice_count": novice_completed_count,
        "junior_count": junior_completed_count,
        "senior_count": senior_completed_count,
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
            faculty = Faculty.objects.get(faculty_id=request.user.username)
            program = faculty.program
            year_section = faculty.year_section
            semester = faculty.semester

            # Create the new student in PostgreSQL
            Student.objects.create(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                middle_initial=middle_initial,
                faculty=faculty,
                program=program,
                year_section=year_section,
                semester=semester,
                student_status='Registered'  # Set default status
            )

            messages.success(request, f"Student {student_id} added successfully!")
            return redirect("faculty-student-list")
        else:
            context = {
                "form": form,
                "show_add_modal": True,
            }
            return render(request, "Students/contents/student-list-content.html", context)
    return redirect("faculty-student-list")

@faculty_required
def edit_student(request, student_id):
    """Update student details in PostgreSQL"""
    student = get_object_or_404(Student, student_id=student_id)

    if request.method == "POST":
        student.first_name = request.POST.get("first_name")
        student.last_name = request.POST.get("last_name")
        student.middle_initial = request.POST.get("middle_initial")
        student.program = request.POST.get("program")
        student.year_section = request.POST.get("year_section")
        student.semester = request.POST.get("semester")

        student.save()

        messages.success(request, "Student details updated successfully!")
        return redirect("faculty-student-list")

    context = {"student": student}
    return render(request, "Students/edit_student.html", context)

@faculty_required
def archived_students_list_page(request):
    """
    Displays a list of students archived by the currently logged-in faculty.
    Handles search and HTMX requests.
    """
    # Get the Faculty profile by matching faculty_id with the user's username
    faculty_profile = get_object_or_404(Faculty, faculty_id=request.user.username)

    # Base queryset for archived students belonging to this faculty
    archived_students_query = ArchivedStudent.objects.filter(faculty=faculty_profile)

    # Handle search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        archived_students_query = archived_students_query.filter(
            Q(student_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(program__icontains=search_query)
        )

    context = {
        "archived_students": archived_students_query.order_by('-archived_at'),
        "search_query": search_query,
    }

    # Handle HTMX requests for partial page updates
    if request.headers.get('HX-Request'):
        return render(request, "Students/contents/students-archived-content.html", context)
    
    # Handle standard requests for a full page load
    return render(request, "Students/students-archived.html", context)


@faculty_required
def Verify_Student(request):
    # Get the logged-in faculty member
    faculty = get_object_or_404(Faculty, faculty_id=request.user.username)

    # Filter pending students that match the faculty's class assignments
    pending_students_query = PendingStudent.objects.filter(
        program=faculty.program,
        year_section=faculty.year_section,
        semester=faculty.semester
    ).order_by('submitted_at')

    # --- Server-side search ---
    search_query = request.GET.get('search', '').strip()
    if search_query:
        pending_students_query = pending_students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    context = {
        "verify_students": pending_students_query,
        "search_query": search_query,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/students-verify-list-content.html', context)
    else:
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
    faculty = get_object_or_404(Faculty, faculty_id=request.user.username)
    pending_student = get_object_or_404(PendingStudent, student_id=student_id)

    try:
        new_student = Student.objects.create(
            student_id=pending_student.student_id,
            first_name=pending_student.first_name,
            last_name=pending_student.last_name,
            middle_initial=pending_student.middle_initial,
            faculty=faculty,
            program=pending_student.program,
            year_section=pending_student.year_section,
            semester=pending_student.semester,
            student_status='Registered',
            password=pending_student.password  # If you want to transfer password
        )
        # If you use Django's set_password, do it here (optional)
        # new_student.set_password(pending_student.password)
        # new_student.save()

        pending_student.delete()
        messages.success(request, f"Student {new_student.first_name} {new_student.last_name} has been accepted.")
    except Exception as e:
        messages.error(request, f"An error occurred while accepting the student: {e}")

    return redirect('verify-students')

@faculty_required
def reject_student(request, student_id):
    pending_student = get_object_or_404(PendingStudent, student_id=student_id)
    try:
        pending_student.delete()
        messages.success(request, f"Registration for student {pending_student.first_name} {pending_student.last_name} has been rejected.")
    except Exception as e:
        messages.error(request, f"An error occurred while rejecting the student: {e}")

    return redirect('verify-students')


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

    if request.method == "POST":
        updates = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'middle_initial': request.POST.get('middle_initial'),
        }
        try:
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
    # Get the logged-in faculty member from PostgreSQL
    try:
        faculty = Faculty.objects.get(faculty_id=request.user.username)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('some_error_page') # Or faculty login

    # Get filter and search parameters from the request
    status_filter = request.GET.get('status', 'all').lower()
    search_query = request.GET.get('search', '').strip()

    # Base query for students assigned to this faculty with non-registered statuses
    students_query = Student.objects.filter(
        faculty=faculty,
        student_status__in=['Completed', 'Dropped']
    )

    # Apply status filter
    if status_filter == 'completed':
        students_query = students_query.filter(student_status='Completed')
    elif status_filter in ['drop-out', 'dropout', 'dropped']:
        students_query = students_query.filter(student_status='Dropped')

    # Apply search filter
    if search_query:
        students_query = students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    students_query = students_query.order_by('-student_id')

    # Pagination
    paginator = Paginator(students_query, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "students": page_obj,
        "faculty_data": faculty,
        "status_filter": status_filter,
        "search_query": search_query,
        "page_obj": page_obj,
        "paginator": paginator,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/student-status-content.html', context)
    else:
        return render(request, 'Students/student-status.html', context)