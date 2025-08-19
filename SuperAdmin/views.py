from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from django.contrib.auth.hashers import make_password
from Faculty.models import Faculty, ArchivedFaculty
from django.http import JsonResponse
from django.templatetags.static import static
from Login.decorators import superadmin_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
import json, datetime
from django.core.paginator import Paginator
from .forms import AddFacultyForm
from django.db import transaction
from Student.models import Student, ArchivedStudent # Add ArchivedStudent
from django.db.models import Q # Import Q for complex queries



# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("C:/Users/ASUS/Desktop/Super_Admin/sentinels-repository/sentinels-a61ff-firebase-adminsdk-fbsvc-35c84e60a7.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# This is the Home page
@superadmin_required
def Superadmin_Home(request):
    db = firestore.client()

    # Total students (PostgreSQL)
    total_students = Student.objects.filter(student_status='Registered').count()

    # Total faculty (PostgreSQL)
    total_faculty = Faculty.objects.filter(faculty_status='Continuing').count()

    # Computer Science students (PostgreSQL)
    cs_students_count = Student.objects.filter(student_status='Registered', faculty__program='Computer Science').count()

    # Information Technology students (PostgreSQL)
    it_students_count = Student.objects.filter(student_status='Registered', faculty__program='Information Technology').count()

    # Task maps for each tier (same as Faculty_Home)
    novice_tasks = [
        "Novice_Task_1(Collect Books)",
        "Novice_Task_2(Collect USB)", 
        "Novice_Task_3(QNA)",
        "Novice_Task_4_(Defeat Rootkit)"
    ]
    junior_tasks = [
        "Junior_Task_1(Domain Research)",
        "Junior_Task_2(Analyze Email)",
        "Junior_Task_3(Security Policy)", 
        "Junior_Task_4(Social Engineering)"
    ]
    senior_tasks = [
        "Senior_Task_1(Threat Landscape)",
        "Senior_Task_2(Malware Ontology)",
        "Senior_Task_3(Incident Response)",
        "Senior_Task_4(AI Malware)"
    ]

    # Initialize tier completion counters
    cs_tier_counts = [0, 0, 0]  # [novice, junior, senior]
    it_tier_counts = [0, 0, 0]  # [novice, junior, senior]

    # Process Computer Science students
    cs_students_query = db.collection("Registered_Students") \
        .where("program", "==", "Computer Science") \
        .stream()

    for doc in cs_students_query:
        student_data = doc.to_dict()
        
        # Check Novice tier completion (all 4 tasks must be completed)
        novice_completed = all(
            student_data.get(task_key, {}).get("points", 0) > 0 
            for task_key in novice_tasks
        )
        if novice_completed:
            cs_tier_counts[0] += 1

        # Check Junior tier completion
        junior_completed = all(
            student_data.get(task_key, {}).get("points", 0) > 0 
            for task_key in junior_tasks
        )
        if junior_completed:
            cs_tier_counts[1] += 1

        # Check Senior tier completion
        senior_completed = all(
            student_data.get(task_key, {}).get("points", 0) > 0 
            for task_key in senior_tasks
        )
        if senior_completed:
            cs_tier_counts[2] += 1

    # Process Information Technology students
    it_students_query = db.collection("Registered_Students") \
        .where("program", "==", "Information Technology") \
        .stream()

    for doc in it_students_query:
        student_data = doc.to_dict()
        
        # Check Novice tier completion
        novice_completed = all(
            student_data.get(task_key, {}).get("points", 0) > 0 
            for task_key in novice_tasks
        )
        if novice_completed:
            it_tier_counts[0] += 1

        # Check Junior tier completion
        junior_completed = all(
            student_data.get(task_key, {}).get("points", 0) > 0 
            for task_key in junior_tasks
        )
        if junior_completed:
            it_tier_counts[1] += 1

        # Check Senior tier completion
        senior_completed = all(
            student_data.get(task_key, {}).get("points", 0) > 0 
            for task_key in senior_tasks
        )
        if senior_completed:
            it_tier_counts[2] += 1

    print(f"Debug - CS tier counts: {cs_tier_counts}")
    print(f"Debug - IT tier counts: {it_tier_counts}")

    context = {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "tier_labels": ["Novice", "Junior", "Senior"],
        "cs_tier_data": cs_tier_counts,
        "it_tier_data": it_tier_counts,
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Home/contents/superadmin-home-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Home/superadmin-home.html', context)
# This is the Faculty list page
@superadmin_required
def Faculty_list(request):

    # Total students (PostgreSQL)
    total_students = Student.objects.filter(student_status='Registered').count()

    # Total faculty (PostgreSQL)
    total_faculty = Faculty.objects.filter(faculty_status='Continuing').count()

    # Computer Science students (PostgreSQL)
    cs_students_count = Student.objects.filter(student_status='Registered', faculty__program='Computer Science').count()

    # Information Technology students (PostgreSQL)
    it_students_count = Student.objects.filter(student_status='Registered', faculty__program='Information Technology').count()

    # Only fetch faculty with status 'Continuing'
    continuing_faculties = Faculty.objects.filter(faculty_status='Continuing').values(
        'faculty_id', 'first_name', 'middle_initial', 'last_name',
        'program', 'year_section', 'semester'
    )
    # Add status field for template compatibility
    continuing_faculties = [
        {**dict(faculty), 'status': 'Continuing'} for faculty in continuing_faculties
    ]

    search_query = request.GET.get('search', '').strip().lower()

    # Server-side search (only on continuing faculty)
    if search_query:
        faculties = [
            f for f in continuing_faculties
            if search_query in str(f.get('first_name', '')).lower()
            or search_query in str(f.get('last_name', '')).lower()
            or search_query in str(f.get('faculty_id', '')).lower()
            or search_query in str(f.get('program', '')).lower()
        ]
    else:
        faculties = continuing_faculties

    faculties = sorted(
        faculties,
        key=lambda s: str(s.get('first_name', '')).lower()
    )

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(faculties, 10)  # 10 faculty per page
    page_obj = paginator.get_page(page_number)

    faculty_count = Faculty.objects.count()  # Now from PostgreSQL

    context = {
        "faculties": page_obj.object_list,
        "total_students": total_students,
        "total_faculty": total_faculty,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "search_query": request.GET.get('search', ''),
        "page_obj": page_obj,
        "paginator": paginator,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Faculty/contents/faculty-list-content.html', context)
    else:
        return render(request, 'Faculty/faculty-list.html', context)
# This is the Faculty add process
@superadmin_required
def add_faculty(request):
    if request.method == "POST":
        form = AddFacultyForm(request.POST)
        if form.is_valid():
            faculty_data = form.cleaned_data
            # Set a default password (hashed). You can change this logic as needed.
            default_password = "welcomeadmin"
            hashed_password = make_password(default_password)
            Faculty.objects.create(
                faculty_id=faculty_data["faculty_id"],
                first_name=faculty_data["first_name"],
                last_name=faculty_data["last_name"],
                middle_initial=faculty_data["middle_initial"],
                program=faculty_data["program"],
                year_section=faculty_data["year_section"],
                semester=faculty_data["semester"],
                password=hashed_password,
            )
            messages.success(request, "Faculty added successfully!")
            return redirect("FacultyList")
        else:
            # Render the faculty list page with errors and open the modal
            faculties = Faculty.objects.all()
            context = {
                "faculties": faculties,
                "form": form,
                "show_add_modal": True,
            }
            return render(request, 'Faculty/faculty-list.html', context)
    else:
        return redirect("FacultyList")
# This is the Faculty edit process
@superadmin_required
def edit_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, faculty_id=faculty_id)

    if request.method == "POST":
        faculty.first_name = request.POST.get("first_name")
        faculty.last_name = request.POST.get("last_name")
        faculty.middle_initial = request.POST.get("middle_initial")
        faculty.program = request.POST.get("program")
        faculty.year_section = request.POST.get("year_section")
        faculty.semester = request.POST.get("semester")
        faculty.save()

        messages.success(request, "Faculty details updated successfully!")
        return redirect("FacultyList")  # or your faculty list page name

    # If you want to render a separate edit page (not used in modal pattern)
    return render(request, "Admin/EditFaculty.html", {"faculty": faculty})
# This is the Faculty delete process
@superadmin_required
@require_POST
def delete_archived_faculty(request, faculty_id):
    try:
        archived_faculty = get_object_or_404(ArchivedFaculty, faculty_id=faculty_id)
        archived_faculty.delete()
        messages.success(request, "Archived faculty deleted permanently.")
    except ArchivedFaculty.DoesNotExist:
        messages.error(request, "Faculty not found in the archive.")
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        
    return redirect('Faculty_Archived')
# This is the Student Archive process
@superadmin_required
@require_POST
def delete_archived_student(request, student_id):
    db.collection("Archived Students").document(student_id).delete()
    messages.success(request, "Archived student deleted permanently.")
    return redirect('superadmin_student_archived')
# This is the Faculty Archive process
@superadmin_required
def Faculty_Archive(request, faculty_id):
    """Move faculty member to ArchivedFaculty table in PostgreSQL"""
    try:
        faculty = Faculty.objects.get(faculty_id=faculty_id)
        # Create archived faculty record
        ArchivedFaculty.objects.create(
            faculty_id=faculty.faculty_id,
            first_name=faculty.first_name,
            last_name=faculty.last_name,
            middle_initial=faculty.middle_initial,
            program=faculty.program,
            year_section=faculty.year_section,
            semester=faculty.semester,
            faculty_status='Archived'
            # Add other fields as needed
        )
        faculty.delete()
        messages.success(request, "Faculty member has been archived successfully!")
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty member not found.")

    return redirect("FacultyList")
# This is the Student Archive process
@superadmin_required
def Superadmin_Student_Archive(request):
    search_query = request.GET.get('search', '').strip()

    # Base query for archived students, pre-fetching related faculty data
    archived_students_query = ArchivedStudent.objects.select_related('faculty').all()

    # Apply search filter if a query is provided
    if search_query:
        archived_students_query = archived_students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )
    
    # Order by the date they were archived
    archived_students_query = archived_students_query.order_by('-archived_at')

    # Pagination
    paginator = Paginator(archived_students_query, 10) # 10 students per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "archived_students": page_obj,
        "search_query": search_query,
        "page_obj": page_obj,
        "paginator": paginator,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/superadmin-archived-students-content.html', context)
    else:
        return render(request, 'Students/superadmin-archived-students.html', context)
# This is the Faculty Archive list page
@superadmin_required
def Archived_faculty_list(request):
    search_query = request.GET.get('search', '').strip()
    
    archived_faculties_query = ArchivedFaculty.objects.all()

    if search_query:
        archived_faculties_query = archived_faculties_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(faculty_id__icontains=search_query)
        )

    archived_faculties_query = archived_faculties_query.order_by('-archived_at')

    paginator = Paginator(archived_faculties_query, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "archived_faculties": page_obj,
        "search_query": search_query,
        "page_obj": page_obj,
        "paginator": paginator,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Faculty/contents/faculty-archived-content.html', context)
    return render(request, 'Faculty/faculty-archived.html', context)
# This is the Faculty restore process
@superadmin_required
def restore_faculty(request, faculty_id):
    try:
        archived_faculty = ArchivedFaculty.objects.get(faculty_id=faculty_id)
        # Move to Faculty table
        Faculty.objects.create(
            faculty_id=archived_faculty.faculty_id,
            first_name=archived_faculty.first_name,
            last_name=archived_faculty.last_name,
            middle_initial=archived_faculty.middle_initial,
            program=archived_faculty.program,
            year_section=archived_faculty.year_section,
            semester=archived_faculty.semester,
            password='',  # Set a default or handle as needed
            faculty_status='Continuing'
        )
        archived_faculty.delete()
        messages.success(request, "Faculty member has been restored successfully!")
    except ArchivedFaculty.DoesNotExist:
        messages.error(request, "Faculty member not found in archive.")

    return redirect("archive-page")
#This is the activity page for the superadmin
def Superadmin_activity_page(request):
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

    # Add this after initializing db = firestore.client()
    game_triggers_ref = db.collection("Game Triggers")
    doc_map = {
        'Novice': 'Novice State',
        'Junior': 'Junior State',
        'Senior': 'Senior State'
    }
    # Fetch all lock states
    lock_states = {}
    for tier, doc_name in doc_map.items():
        doc = game_triggers_ref.document(doc_name).get()
        if doc.exists:
            lock_states[tier] = doc.to_dict().get(f"{tier} isLock", True)  # Default to locked
        else:
            lock_states[tier] = True

    # Add isLock to each activity based on the tier lock
    for activity in activities_novice:
        activity['isLock'] = lock_states['Novice']
    for activity in activities_junior:
        activity['isLock'] = lock_states['Junior']
    for activity in activities_senior:
        activity['isLock'] = lock_states['Senior']

    context = {
        "activities_novice": activities_novice,
        "activities_junior": activities_junior,
        "activities_senior": activities_senior,
        "novice_is_locked": lock_states['Novice'],
        "junior_is_locked": lock_states['Junior'],
        "senior_is_locked": lock_states['Senior'],
        "show_sticky_container": False,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Activities/contents/Superadmin-Activity-List-content.html', context)
    else:
        return render(request, 'Activities/Superadmin-Activity-List.html', context)
# This is the Student Status page
@superadmin_required
def Superadmin_Student_Status(request):

    # Total students (PostgreSQL)
    total_students = Student.objects.filter(student_status='Registered').count()

    # Computer Science students (PostgreSQL)
    cs_students_count = Student.objects.filter(student_status='Registered', faculty__program='Computer Science').count()

    # Information Technology students (PostgreSQL)
    it_students_count = Student.objects.filter(student_status='Registered', faculty__program='Information Technology').count()


    # Get filter parameters from the request
    status_filter = request.GET.get('status', 'all')
    program_filter = request.GET.get('program', 'all')
    year_section_filter = request.GET.get('year_section', 'all')
    semester_filter = request.GET.get('semester', 'all')
    search_query = request.GET.get('search', '').strip()

    # Start with a base query for all students, pre-fetching faculty data
    students_query = Student.objects.select_related('faculty').all()

    # Apply filters based on user selection
    if status_filter != 'all':
        # Map the filter value to the model's choices
        status_map = {
            'registered': 'Registered',
            'completed': 'Completed',
            'dropout': 'Drop-out'
        }
        if status_filter in status_map:
            students_query = students_query.filter(student_status=status_map[status_filter])

    if program_filter != 'all':
        students_query = students_query.filter(faculty__program=program_filter)
    
    if year_section_filter != 'all':
        students_query = students_query.filter(faculty__year_section=year_section_filter)
        
    if semester_filter != 'all':
        students_query = students_query.filter(faculty__semester=semester_filter)

    if search_query:
        students_query = students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    # Get unique year sections for the filter dropdown
    year_sections = sorted(list(Faculty.objects.values_list('year_section', flat=True).distinct()))

    # Order the results
    students_query = students_query.order_by('last_name', 'first_name')

    # Pagination
    paginator = Paginator(students_query, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "students": page_obj,
        "status_filter": status_filter,
        "program_filter": program_filter,
        "year_section_filter": year_section_filter,
        "semester_filter": semester_filter,
        "year_sections": year_sections,
        "search_query": search_query,
        "page_obj": page_obj,
        "paginator": paginator,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        'total_students': total_students,
        'active_count': total_students,

    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/superadmin-student-status-content.html', context)
    else:
        return render(request, 'Students/superadmin-student-status.html', context)
# This is the Faculty Status page
@superadmin_required
def Faculty_Status(request):

    # Total students (PostgreSQL)
    total_students = Student.objects.filter(student_status='Registered').count()

    # Total faculty (PostgreSQL)
    total_faculty = Faculty.objects.filter(faculty_status='Continuing').count()

    # Computer Science students (PostgreSQL)
    cs_students_count = Student.objects.filter(student_status='Registered', faculty__program='Computer Science').count()

    # Information Technology students (PostgreSQL)
    it_students_count = Student.objects.filter(student_status='Registered', faculty__program='Information Technology').count()

    status_filter = request.GET.get('status', 'all')
    program_filter = request.GET.get('program', 'all')
    year_section_filter = request.GET.get('year_section', 'all')
    semester_filter = request.GET.get('semester', 'all')
    search_query = request.GET.get('search', '').strip().lower()

    # Fetch all faculty from PostgreSQL
    faculties = Faculty.objects.all()

    # Apply status filter
    if status_filter != 'all':
        faculties = faculties.filter(faculty_status=status_filter)

    # Apply program filter
    if program_filter != 'all':
        faculties = faculties.filter(program=program_filter)

    # Apply year_section filter
    if year_section_filter != 'all':
        faculties = faculties.filter(year_section=year_section_filter)

    # Apply semester filter
    if semester_filter != 'all':
        faculties = faculties.filter(semester=semester_filter)

    # Apply search filter
    if search_query:
        faculties = faculties.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(faculty_id__icontains=search_query) |
            models.Q(program__icontains=search_query)
        )

    # Gather unique values for dropdowns
    year_sections = sorted(set(faculties.values_list('year_section', flat=True)))
    programs = sorted(set(faculties.values_list('program', flat=True)))
    semesters = sorted(set(faculties.values_list('semester', flat=True)))

    # Sort alphabetically by first name
    faculties = faculties.order_by('first_name')

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(faculties, 12)
    page_obj = paginator.get_page(page_number)

    context = {
        "faculties": page_obj.object_list,
        "status_filter": status_filter,
        "program_filter": program_filter,
        "year_section_filter": year_section_filter,
        "semester_filter": semester_filter,
        "programs": programs,
        "year_sections": year_sections,
        "semesters": semesters,
        "search_query": request.GET.get('search', ''),
        "page_obj": page_obj,
        "paginator": paginator,
        "total_students": total_students,
        "total_faculty": total_faculty,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Faculty/contents/faculty-status-content.html', context)
    else:
        return render(request, 'Faculty/faculty-status.html', context)
# This is the Faculty move process
@superadmin_required
@require_POST
def move_faculty(request):
    faculty_id = request.POST.get("faculty_id")
    destination = request.POST.get("destination")

    try:
        with transaction.atomic():
            # First, check if faculty exists in either active or archived table
            faculty = Faculty.objects.filter(faculty_id=faculty_id).first()
            archived_faculty = ArchivedFaculty.objects.filter(faculty_id=faculty_id).first()

            if not faculty and not archived_faculty:
                messages.error(request, "Faculty not found.")
                return redirect(request.META.get('HTTP_REFERER', 'Faculty_list'))

            # Case 1: Moving within Active table (between Continuing and Completed)
            if destination in ["continuing", "completed"] and faculty:
                faculty.faculty_status = destination.capitalize()
                faculty.save()
                messages.success(request, f"Faculty status updated to '{faculty.faculty_status}'.")

            # Case 2: Restoring from Archive to Active
            elif destination in ["continuing", "completed"] and archived_faculty:
                Faculty.objects.create(
                    faculty_id=archived_faculty.faculty_id,
                    first_name=archived_faculty.first_name,
                    last_name=archived_faculty.last_name,
                    middle_initial=archived_faculty.middle_initial,
                    program=archived_faculty.program,
                    year_section=archived_faculty.year_section,
                    semester=archived_faculty.semester,
                    password='',  # A new password should be set upon restoration
                    faculty_status=destination.capitalize()
                )
                archived_faculty.delete()
                messages.success(request, f"Faculty restored to '{destination.capitalize()}' status.")

            # Case 3: Moving from Active to Archive (Deactivating)
            elif destination == "archive" and faculty:
                ArchivedFaculty.objects.create(
                    faculty_id=faculty.faculty_id,
                    first_name=faculty.first_name,
                    last_name=faculty.last_name,
                    middle_initial=faculty.middle_initial,
                    program=faculty.program,
                    year_section=faculty.year_section,
                    semester=faculty.semester
                )
                faculty.delete()
                messages.success(request, "Faculty has been archived (deactivated) successfully.")
            
            # Case 4: Already in archive
            elif destination == "archive" and archived_faculty:
                messages.info(request, "Faculty is already archived.")
            
            else:
                messages.error(request, "Invalid operation specified.")

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")

    referer = request.META.get('HTTP_REFERER', 'Faculty_list')
    return redirect(referer)
# This is the Student List page
@superadmin_required
def Superadmin_Student_List(request):

    # Total students (PostgreSQL)
    total_students = Student.objects.filter(student_status='Registered').count()

    # Computer Science students (PostgreSQL)
    cs_students_count = Student.objects.filter(student_status='Registered', faculty__program='Computer Science').count()

    # Information Technology students (PostgreSQL)
    it_students_count = Student.objects.filter(student_status='Registered', faculty__program='Information Technology').count()


    # Get filter parameters
    selected_program = request.GET.get('program', 'all')
    selected_year_section = request.GET.get('year_section', 'all')
    selected_semester = request.GET.get('semester', 'all')
    search_query = request.GET.get('search', '').strip()

    # Base query: all students with related faculty data to prevent N+1 queries
    students_query = Student.objects.select_related('faculty').filter(student_status='Registered')

    # Apply filters using Django ORM
    if selected_program != 'all':
        students_query = students_query.filter(faculty__program=selected_program)
    if selected_year_section != 'all':
        students_query = students_query.filter(faculty__year_section=selected_year_section)
    if selected_semester != 'all':
        students_query = students_query.filter(faculty__semester=selected_semester)
    
    if search_query:
        students_query = students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )


    # Pagination
    paginator = Paginator(students_query, 10)  # 10 students per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'students': page_obj,
        'total_students': total_students,
        'active_count': total_students, # 'Registered' students are considered active
        'selected_program': selected_program,
        'selected_year_section': selected_year_section,
        'selected_semester': selected_semester,
        'search_query': search_query,
        'page_obj': page_obj,
        'paginator': paginator,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/superadmin-student-list-content.html', context)
    else:
        return render(request, 'Students/superadmin-student-list.html', context)
# This is the Game Trigger update process
@superadmin_required
@csrf_exempt
def update_game_trigger(request):
    if request.method == "POST":
        data = json.loads(request.body)
        tier = data.get('tier')
        task = data.get('task')
        isLock = data.get('isLock')

        # Map tier to document name
        doc_map = {
            'Novice': 'Novice State',
            'Junior': 'Junior State',
            'Senior': 'Senior State'
        }
        doc_name = doc_map.get(tier)
        if not doc_name or not task:
            return JsonResponse({'success': False, 'error': 'Invalid data'})

        key_name = f"{task} isLock"
        db.collection("Game Triggers").document(doc_name).set(
            {key_name: isLock}, merge=True
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
# This is the Tier Lock update process
@superadmin_required
@csrf_exempt
def update_tier_lock(request):
    if request.method == "POST":
        data = json.loads(request.body)
        tier = data.get('tier')
        isLock = data.get('isLock')

        doc_map = {
            'Novice': 'Novice State',
            'Junior': 'Junior State',
            'Senior': 'Senior State'
        }
        doc_name = doc_map.get(tier)
        if not doc_name:
            return JsonResponse({'success': False, 'error': 'Invalid tier'})

        # Set only one key per tier
        update_data = {f"{tier} isLock": isLock}

        db.collection("Game Triggers").document(doc_name).set(update_data, merge=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
# This is the Student Move process
@superadmin_required
def superadmin_move_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        destination = request.POST.get("destination")

        # Find the student in either the active or archived table
        student = Student.objects.filter(student_id=student_id).first()
        archived_student = ArchivedStudent.objects.filter(student_id=student_id).first()

        if not student and not archived_student:
            messages.error(request, "Student not found.")
            return redirect(request.META.get('HTTP_REFERER', 'Superadmin_Student_Status'))

        try:
            with transaction.atomic():
                # Destination is one of the active statuses
                if destination in ["registered", "completed", "dropout"]:
                    new_status = {
                        "registered": "Registered",
                        "completed": "Completed",
                        "dropout": "Drop-out"
                    }.get(destination)

                    if student:
                        # Student is already active, just update status
                        student.student_status = new_status
                        student.save()
                        messages.success(request, f"Student status updated to {new_status}.")
                    elif archived_student:
                        # Student is archived, so restore to active table
                        Student.objects.create(
                            student_id=archived_student.student_id,
                            first_name=archived_student.first_name,
                            last_name=archived_student.last_name,
                            middle_initial=archived_student.middle_initial,
                            faculty=archived_student.faculty,
                            student_status=new_status
                        )
                        archived_student.delete()
                        messages.success(request, f"Student restored and moved to {new_status}.")

                # Destination is the archive
                elif destination == "archive":
                    if student:
                        # Move from active to archive
                        ArchivedStudent.objects.create(
                            student_id=student.student_id,
                            first_name=student.first_name,
                            last_name=student.last_name,
                            middle_initial=student.middle_initial,
                            faculty=student.faculty
                        )
                        student.delete()
                        messages.success(request, "Student moved to Archive successfully.")
                    elif archived_student:
                        # Already in archive
                        messages.info(request, "Student is already in the archive.")
                
                else:
                    messages.error(request, "Invalid destination specified.")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        # Redirect back to the page the user came from
        return redirect(request.META.get('HTTP_REFERER', 'Superadmin_Student_Status'))

    # Redirect if not a POST request
    return redirect('Superadmin_Student_Status')