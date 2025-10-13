from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from django.contrib.auth.hashers import make_password
from Faculty.models import Faculty, ArchivedFaculty, FacultyAssignment
from django.http import JsonResponse
from django.templatetags.static import static
from Login.decorators import superadmin_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.core.paginator import Paginator
from .forms import AddFacultyForm
from django.db import transaction
from Student.models import Student, ArchivedStudent
from django.db.models import Q # Import Q for complex queries
import io

#Import CSV and Excel libraries
import csv
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from openpyxl import load_workbook
from django.http import HttpResponse

from django.db.models import Prefetch






# Firestore database instance
from SentinelsProject.firebase_config import db

# This is the Home page
@superadmin_required
def Superadmin_Home(request):
    db = firestore.client()

    # Total students (PostgreSQL)
    total_students = Student.objects.filter(student_status='Registered').count()

    # Total faculty (PostgreSQL)
    total_faculty = Faculty.objects.filter(faculty_status='Continuing').count()

    # Computer Science students (PostgreSQL) - UPDATED
    cs_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Computer Science').count()

    # Information Technology students (PostgreSQL) - UPDATED
    it_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Information Technology').count()

    # Task maps for each tier (same as Faculty_Home)
    novice_tasks = [
        "Novice_Task_1(Collect Books)",
        "Novice_Task_2(Collect USB)", 
        "Novice_Task_3(QNA)",
        "Novice_Task_4_(Defeat Rootkit)"
    ]
    junior_tasks = [
        "Junior_Task_1(Collect Books",
        "Junior_Task_2(QNA)",
        "Junior_Task_3(Security Policy)", 
        "Junior_Task_4(Social Engineering)"
        "Junior_Task_5()"
        "Junior_Task_6()"
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

    total_students = Student.objects.filter(student_status='Registered').count()
    total_faculty = Faculty.objects.filter(faculty_status='Continuing').count()
    cs_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Computer Science').count()
    it_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Information Technology').count()

    # Get filter values from request
    program_filter = request.GET.get('program', 'all')
    year_section_filter = request.GET.get('year_section', 'all')
    semester_filter = request.GET.get('semester', 'all')

    faculty_query = Faculty.objects.filter(faculty_status='Continuing').prefetch_related(
        Prefetch('assignments', queryset=FacultyAssignment.objects.filter(is_active=True))
    )

    # Dropdown filters for Program, Year & Section, and Semster
    if program_filter != 'all':
        faculty_query = faculty_query.filter(assignments__program=program_filter).distinct()
    
    if year_section_filter != 'all':
        faculty_query = faculty_query.filter(assignments__year_section=year_section_filter).distinct()
    
    if semester_filter != 'all':
        faculty_query = faculty_query.filter(assignments__semester=semester_filter).distinct()

    search_query = request.GET.get('search', '').strip().lower()
    if search_query:
        faculty_query = faculty_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(faculty_id__icontains=search_query) |
            Q(assignments__program__icontains=search_query)
        ).distinct()

    # Get unique sections for the filter dropdown
    sections = FacultyAssignment.objects.filter(
        is_active=True,
        faculty__faculty_status='Continuing'
    ).values_list('year_section', flat=True).distinct().order_by('year_section')

    faculty_query = faculty_query.order_by('first_name')

    page_number = request.GET.get('page', 1)
    paginator = Paginator(faculty_query, 8)
    page_obj = paginator.get_page(page_number)

    context = {
        "faculties": page_obj.object_list,
        "total_students": total_students,
        "total_faculty": total_faculty,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "search_query": request.GET.get('search', ''),
        "page_obj": page_obj,
        "paginator": paginator,
        "program_filter": program_filter,
        "year_section_filter": year_section_filter,
        "semester_filter": semester_filter,
        "sections": sections,
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
            print(f"Form cleaned data: {form.cleaned_data}")
            print(f"Assignments after cleaning: {form.cleaned_data.get('assignments', 'NO ASSIGNMENTS')}")
            
            try:
                with transaction.atomic():
                    faculty = form.save()
                    messages.success(request, f"Faculty {faculty.faculty_id} added successfully!")
                    return redirect("FacultyList")
            except Exception as e:
                print(f"Error during save: {str(e)}")
                messages.error(request, f"Error adding faculty: {str(e)}")
        else:
            print(f"Form errors: {form.errors}")
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            messages.error(request, "; ".join(error_messages))
            
        return redirect("FacultyList")
    else:
        return redirect("FacultyList")

# This is the Faculty edit process
@superadmin_required
def edit_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, faculty_id=faculty_id)

    if request.method == "POST":
        # Update basic faculty information
        faculty.first_name = request.POST.get("first_name")
        faculty.last_name = request.POST.get("last_name")
        faculty.middle_initial = request.POST.get("middle_initial")
        faculty.save()

        # Handle assignments
        assignments_data = request.POST.get("assignments", "[]")
        try:
            assignments = json.loads(assignments_data)
            
            # Get existing assignments
            existing_assignments = {str(a.id): a for a in faculty.assignments.all()}
            processed_ids = set()
            
            # Process each assignment from the form
            for assignment_data in assignments:
                if 'id' in assignment_data and assignment_data['id']:
                    # Update existing assignment
                    assignment_id = str(assignment_data['id'])
                    if assignment_id in existing_assignments:
                        assignment = existing_assignments[assignment_id]
                        assignment.program = assignment_data['program']
                        assignment.year_section = assignment_data['year_section']
                        assignment.semester = assignment_data['semester']
                        assignment.save()
                        processed_ids.add(assignment_id)
                else:
                    # Create new assignment
                    FacultyAssignment.objects.create(
                        faculty=faculty,
                        program=assignment_data['program'],
                        year_section=assignment_data['year_section'],
                        semester=assignment_data['semester']
                    )
            
            # Delete assignments that were removed
            for assignment_id, assignment in existing_assignments.items():
                if assignment_id not in processed_ids:
                    assignment.delete()
                    
        except json.JSONDecodeError:
            messages.error(request, "Invalid assignments data.")
            return redirect("FacultyList")

        messages.success(request, "Faculty details updated successfully!")
        return redirect("FacultyList")

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


@superadmin_required
@require_POST
def superadmin_delete_archived_student(request, student_id):
    try:
        # Delete from Django database (ArchivedStudent model)
        archived_student = ArchivedStudent.objects.get(student_id=student_id)
        archived_student.delete()
        
        # Also delete from Firestore if it exists there
        try:
            db.collection("Archived Students").document(student_id).delete()
        except Exception as firestore_error:
            # Log the error but don't fail the operation
            print(f"Firestore deletion error: {firestore_error}")
        
        messages.success(request, "Archived student deleted permanently.")
    except ArchivedStudent.DoesNotExist:
        messages.error(request, "Archived student not found in database.")
    except Exception as e:
        messages.error(request, f"Error deleting student: {str(e)}")
    
    return redirect('superadmin_student_archived')


# This is the Faculty Archive process
@superadmin_required
def Faculty_Archive(request, faculty_id):
    """Move faculty member to ArchivedFaculty table"""
    try:
        with transaction.atomic():
            faculty = Faculty.objects.get(faculty_id=faculty_id)
            
            assignments = list(faculty.assignments.filter(is_active=True).values(
                'program', 'year_section', 'semester'
            ))
            
            ArchivedFaculty.objects.create(
                faculty_id=faculty.faculty_id,
                first_name=faculty.first_name,
                last_name=faculty.last_name,
                middle_initial=faculty.middle_initial,
                faculty_status='Archived',
                assignments_data=assignments
            )
            
            faculty.delete()
            messages.success(request, "Faculty member has been archived successfully!")
            
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty member not found.")
    except Exception as e:
        messages.error(request, f"Error archiving faculty: {str(e)}")

    return redirect("FacultyList")


@superadmin_required
def Superadmin_Student_Archive(request):

    search_query = request.GET.get('search', '').strip()

    # Base query for archived students with faculty_assignment and faculty relationships
    archived_students_query = ArchivedStudent.objects.select_related('faculty_assignment')

    if search_query:
        archived_students_query = archived_students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(archived_students_query, 10)
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
        with transaction.atomic():
            archived_faculty = ArchivedFaculty.objects.get(faculty_id=faculty_id)
            
            faculty = Faculty.objects.create(
                faculty_id=archived_faculty.faculty_id,
                first_name=archived_faculty.first_name,
                last_name=archived_faculty.last_name,
                middle_initial=archived_faculty.middle_initial,
                password=make_password("welcomeadmin"),
                faculty_status='Continuing'
            )
            
            for assignment_data in archived_faculty.assignments_data:
                FacultyAssignment.objects.create(
                    faculty=faculty,
                    program=assignment_data['program'],
                    year_section=assignment_data['year_section'],
                    semester=assignment_data['semester'],
                    is_active=True
                )
            
            archived_faculty.delete()
            messages.success(request, "Faculty member has been restored successfully!")
            
    except ArchivedFaculty.DoesNotExist:
        messages.error(request, "Faculty member not found in archive.")
    except Exception as e:
        messages.error(request, f"Error restoring faculty: {str(e)}")

    return redirect("Faculty_Archived")



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
    # Total Faculty 
    total_faculty = Faculty.objects.filter(faculty_status='Continuing').count()
    # Computer Science students
    cs_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Computer Science').count()
    # Information Technology students
    it_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Information Technology').count()

   # Get all filter parameters
    selected_program = request.GET.get('program', 'all')
    selected_year_section = request.GET.get('year_section', 'all')
    selected_semester = request.GET.get('semester', 'all')
    selected_status = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '').strip()

    # Base query with related faculty data
    students_query = Student.objects.select_related('faculty_assignment')

    # Count statistics
    total_students = Student.objects.count()
    registered_count = Student.objects.filter(student_status='Registered').count()
    completed_count = Student.objects.filter(student_status='Completed').count()
    dropout_count = Student.objects.filter(student_status='Drop-out').count()

    # Apply filters
    if selected_program != 'all':
        students_query = students_query.filter(faculty_assignment__program=selected_program)
    if selected_year_section != 'all':
        students_query = students_query.filter(faculty_assignment__year_section=selected_year_section)
    if selected_semester != 'all':
        students_query = students_query.filter(faculty_assignment__semester=selected_semester)
    if selected_status != 'all':
        students_query = students_query.filter(student_status=selected_status)
    
    if search_query:
        students_query = students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    # Get distinct sections for the filter dropdown
    sections = Student.objects.values_list(
        'faculty_assignment__year_section', flat=True
    ).distinct().order_by('faculty_assignment__year_section')


    # Pagination
    paginator = Paginator(students_query, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'students': page_obj,
        'sections': sections,
        'selected_program': selected_program,
        'selected_year_section': selected_year_section,
        'selected_semester': selected_semester,
        'selected_status': selected_status,
        'search_query': search_query,
        'total_students': total_students,
        'active_count': total_students,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "total_faculty" : total_faculty,
        'page_obj': page_obj,
        'paginator': paginator,

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
    # Total faculty (PostgreSQL) - Include both Continuing and Completed
    total_faculty = Faculty.objects.filter(faculty_status__in=['Continuing', 'Completed']).count()
    # Computer Science students (PostgreSQL)
    cs_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Computer Science').count()

    # Information Technology students (PostgreSQL)
    it_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Information Technology').count()

    status_filter = request.GET.get('status', 'all')
    program_filter = request.GET.get('program', 'all')
    year_section_filter = request.GET.get('year_section', 'all')
    semester_filter = request.GET.get('semester', 'all')
    search_query = request.GET.get('search', '').strip().lower()

    # Fetch all faculty from PostgreSQL with assignments - Include both Continuing and Completed
    faculty_query = Faculty.objects.filter(
        faculty_status__in=['Continuing', 'Completed', 'Deactivated']
    ).prefetch_related(
        Prefetch('assignments', queryset=FacultyAssignment.objects.filter(is_active=True))
    )

    # Apply status filter
    if status_filter != 'all':
        faculty_query = faculty_query.filter(faculty_status=status_filter)

    # Apply program filter - UPDATED
    if program_filter != 'all':
        faculty_query = faculty_query.filter(assignments__program=program_filter).distinct()

    # Apply year_section filter - UPDATED
    if year_section_filter != 'all':
        faculty_query = faculty_query.filter(assignments__year_section=year_section_filter).distinct()

    # Apply semester filter - UPDATED
    if semester_filter != 'all':
        faculty_query = faculty_query.filter(assignments__semester=semester_filter).distinct()

    # Apply search filter - UPDATED
    if search_query:
        faculty_query = faculty_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(faculty_id__icontains=search_query) |
            Q(assignments__program__icontains=search_query)
        ).distinct()

    # Gather unique values for dropdowns - UPDATED
    sections = FacultyAssignment.objects.filter(
        is_active=True,
        faculty__faculty_status='Continuing'
    ).values_list('year_section', flat=True).distinct().order_by('year_section')

    # Sort alphabetically by first name
    faculty_query = faculty_query.order_by('first_name')

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(faculty_query, 8)
    page_obj = paginator.get_page(page_number)

    context = {
        "faculties": page_obj.object_list,
        "status_filter": status_filter,
        "program_filter": program_filter,
        "year_section_filter": year_section_filter,
        "semester_filter": semester_filter,
        "sections": sections,
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
                # Create the faculty record
                restored_faculty = Faculty.objects.create(
                    faculty_id=archived_faculty.faculty_id,
                    first_name=archived_faculty.first_name,
                    last_name=archived_faculty.last_name,
                    middle_initial=archived_faculty.middle_initial,
                    password=make_password("welcomeadmin"),  # Set default password
                    faculty_status=destination.capitalize()
                )
                
                # Restore assignments from archived data
                if archived_faculty.assignments_data:
                    for assignment_data in archived_faculty.assignments_data:
                        FacultyAssignment.objects.create(
                            faculty=restored_faculty,
                            program=assignment_data.get('program', ''),
                            year_section=assignment_data.get('year_section', ''),
                            semester=assignment_data.get('semester', ''),
                            is_active=True
                        )
                
                archived_faculty.delete()
                messages.success(request, f"Faculty restored to '{destination.capitalize()}' status with all assignments.")

            # Case 3: Moving from Active to Archive (Deactivating)
            elif destination == "archive" and faculty:
                # Collect assignment data before archiving
                assignments = list(faculty.assignments.filter(is_active=True).values(
                    'program', 'year_section', 'semester'
                ))
                
                ArchivedFaculty.objects.create(
                    faculty_id=faculty.faculty_id,
                    first_name=faculty.first_name,
                    last_name=faculty.last_name,
                    middle_initial=faculty.middle_initial,
                    faculty_status='Archived',
                    assignments_data=assignments
                )
                faculty.delete()  # This will cascade delete the assignments too
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


@superadmin_required
def Superadmin_Student_List(request):
    # Total Faculty 
    total_faculty = Faculty.objects.filter(faculty_status='Continuing').count()
    # Computer Science students
    cs_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Computer Science').count()
    # Information Technology students
    it_students_count = Student.objects.filter(student_status='Registered', faculty_assignment__program='Information Technology').count()

    # Get all filter parameters
    selected_program = request.GET.get('program', 'all')
    selected_year_section = request.GET.get('year_section', 'all')
    selected_semester = request.GET.get('semester', 'all')
    search_query = request.GET.get('search', '').strip()

    # Base query with related faculty data
    students_query = Student.objects.select_related('faculty_assignment')

    # Count statistics
    total_students = Student.objects.count()
    registered_count = Student.objects.filter(student_status='Registered').count()
    completed_count = Student.objects.filter(student_status='Completed').count()
    dropout_count = Student.objects.filter(student_status='Drop-out').count()

    # Apply filters
    if selected_program != 'all':
        students_query = students_query.filter(faculty_assignment__program=selected_program)
    if selected_year_section != 'all':
        students_query = students_query.filter(faculty_assignment__year_section=selected_year_section)
    if selected_semester != 'all':
        students_query = students_query.filter(faculty_assignment__semester=selected_semester)
    
    if search_query:
        students_query = students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    # Get distinct sections for the filter dropdown
    sections = Student.objects.values_list(
        'faculty_assignment__year_section', flat=True
    ).distinct().order_by('faculty_assignment__year_section')

    # Pagination
    paginator = Paginator(students_query, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'students': page_obj,
        'sections': sections,
        'selected_program': selected_program,
        'selected_year_section': selected_year_section,
        'selected_semester': selected_semester,
        'search_query': search_query,
        'total_students': total_students,
        'active_count': total_students,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "total_faculty" : total_faculty,
        'page_obj': page_obj,
        'paginator': paginator,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/superadmin-student-list-content.html', context)
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
                        # Student is archived, so restore to active table with faculty_assignment
                        Student.objects.create(
                            student_id=archived_student.student_id,
                            first_name=archived_student.first_name,
                            last_name=archived_student.last_name,
                            middle_initial=archived_student.middle_initial,
                            faculty_assignment=archived_student.faculty_assignment,
                            student_status=new_status
                        )
                        archived_student.delete()
                        messages.success(request, f"Student restored and moved to {new_status}.")

                # Destination is the archive
                elif destination == "archive":
                    if student:
                        # Move from active to archive with faculty_assignment
                        ArchivedStudent.objects.create(
                            student_id=student.student_id,
                            first_name=student.first_name,
                            last_name=student.last_name,
                            middle_initial=student.middle_initial,
                            faculty_assignment=student.faculty_assignment,
                            program=student.faculty_assignment.program if student.faculty_assignment else '',
                            year_section=student.faculty_assignment.year_section if student.faculty_assignment else '',
                            semester=student.faculty_assignment.semester if student.faculty_assignment else ''
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



@superadmin_required
def export_faculty_csv(request):
    """Export faculty data to CSV file with multiple assignments"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="faculty_export.csv"'
    
    writer = csv.writer(response)
    # Write CSV header with Status
    writer.writerow([
        'Faculty ID',
        'First Name', 
        'Last Name',
        'Middle Initial',
        'Program',
        'Year Section',
        'Semester',
        'Status'  # Keep Status in export
    ])
    
    # Write faculty data with multiple assignments
    faculties = Faculty.objects.prefetch_related('assignments').all().order_by('faculty_id')
    for faculty in faculties:
        assignments = faculty.assignments.all()
        if assignments:
            # Write one row per assignment
            for assignment in assignments:
                writer.writerow([
                    faculty.faculty_id,
                    faculty.first_name,
                    faculty.last_name,
                    faculty.middle_initial or '',
                    assignment.program,
                    assignment.year_section,
                    assignment.semester,
                    faculty.faculty_status  # Keep Status in export
                ])
        else:
            # Faculty with no assignments
            writer.writerow([
                faculty.faculty_id,
                faculty.first_name,
                faculty.last_name,
                faculty.middle_initial or '',
                '',
                '',
                '',
                faculty.faculty_status  # Keep Status in export
            ])
    
    return response

@superadmin_required
def export_faculty_excel(request):
    """Export faculty data to Excel file with multiple assignments"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Faculty Export"
    
    # Define headers with Status
    headers = [
        'Faculty ID',
        'First Name', 
        'Last Name',
        'Middle Initial',
        'Program',
        'Year Section',
        'Semester',
        'Status'  # Keep Status in export
    ]
    
    # Style for headers
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Add headers with styling
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Get faculty data and add to worksheet
    faculties = Faculty.objects.prefetch_related('assignments').all().order_by('faculty_id')
    row = 2
    
    for faculty in faculties:
        assignments = faculty.assignments.all()
        if assignments:
            # Write one row per assignment
            for assignment in assignments:
                data = [
                    faculty.faculty_id,
                    faculty.first_name,
                    faculty.last_name,
                    faculty.middle_initial or '',
                    assignment.program,
                    assignment.year_section,
                    assignment.semester,
                    faculty.faculty_status  # Keep Status in export
                ]
                
                for col, value in enumerate(data, 1):
                    cell = ws.cell(row=row, column=col, value=value)
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    
                    # Status color coding
                    if col == 8:  # Status column
                        if value == 'Completed':
                            cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
                        elif value == 'Deactivated':
                            cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
                        else:  # Continuing
                            cell.fill = PatternFill(start_color="E8F5E8", end_color="E8F5E8", fill_type="solid")
                
                row += 1
        else:
            # Faculty with no assignments
            data = [
                faculty.faculty_id,
                faculty.first_name,
                faculty.last_name,
                faculty.middle_initial or '',
                '',
                '',
                '',
                faculty.faculty_status  # Keep Status in export
            ]
            
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col, value=value)
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            row += 1
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxWmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="faculty_export.xlsx"'
    
    wb.save(response)
    return response

#  Import for Faculty
@superadmin_required
def import_faculty(request):
    """Import faculty data from CSV or Excel file with multiple assignments"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        uploaded_file = request.FILES['csv_file']
        
        # Get file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Validate file type
        if file_extension not in ['csv', 'xlsx', 'xls']:
            messages.error(request, 'Please upload a CSV or Excel file (.csv, .xlsx, .xls).')
            return redirect('FacultyList')
        
        try:
            success_count = 0
            error_count = 0
            errors = []
            faculty_data = {}  # To group assignments by faculty_id
            
            # Process based on file type
            if file_extension == 'csv':
                file_data = uploaded_file.read().decode('utf-8')
                io_string = io.StringIO(file_data)
                reader = csv.DictReader(io_string)
                rows = list(reader)
            else:
                workbook = load_workbook(uploaded_file, read_only=True)
                worksheet = workbook.active
                
                headers = [cell.value for cell in worksheet[1]]
                rows = []
                for row in worksheet.iter_rows(min_row=2, values_only=True):
                    if any(row):  # Skip empty rows
                        row_dict = {}
                        for i, value in enumerate(row):
                            if i < len(headers) and headers[i]:
                                row_dict[headers[i]] = str(value) if value is not None else ''
                        rows.append(row_dict)
            
            # Group rows by faculty_id
            for row_num, row in enumerate(rows, start=2):
                try:
                    faculty_id = row.get('Faculty ID', '').strip()
                    first_name = row.get('First Name', '').strip()
                    last_name = row.get('Last Name', '').strip()
                    middle_initial = row.get('Middle Initial', '').strip()
                    program = row.get('Program', '').strip()
                    year_section = row.get('Year Section', '').strip()
                    semester = row.get('Semester', '').strip()
                    
                    # Validate required fields
                    if not faculty_id:
                        errors.append(f'Row {row_num}: Faculty ID is required')
                        error_count += 1
                        continue
                    
                    if not all([first_name, last_name]) and faculty_id not in faculty_data:
                        errors.append(f'Row {row_num}: First Name and Last Name are required for new faculty')
                        error_count += 1
                        continue
                    
                    # Initialize faculty data if not exists
                    if faculty_id not in faculty_data:
                        faculty_data[faculty_id] = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'middle_initial': middle_initial,
                            'assignments': []
                        }
                    
                    # Add assignment if program data is provided
                    if program and year_section and semester:
                        # Validate program
                        if program not in ['Computer Science', 'Information Technology']:
                            errors.append(f'Row {row_num}: Invalid program "{program}"')
                            error_count += 1
                            continue
                        
                        faculty_data[faculty_id]['assignments'].append({
                            'program': program,
                            'year_section': year_section,
                            'semester': semester
                        })
                    
                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')
                    error_count += 1
                    continue
            
            # Create/Update faculty with their assignments
            for faculty_id, data in faculty_data.items():
                try:
                    with transaction.atomic():
                        # Check if faculty already exists
                        faculty, created = Faculty.objects.get_or_create(
                            faculty_id=faculty_id,
                            defaults={
                                'first_name': data['first_name'],
                                'last_name': data['last_name'],
                                'middle_initial': data['middle_initial'],
                                'password': make_password("welcomeadmin"),
                                'faculty_status': 'Continuing'  # Default status
                            }
                        )
                        
                        if created:
                            success_count += 1
                            
                            # Create assignments for new faculty
                            for assignment_data in data['assignments']:
                                FacultyAssignment.objects.create(
                                    faculty=faculty,
                                    program=assignment_data['program'],
                                    year_section=assignment_data['year_section'],
                                    semester=assignment_data['semester']
                                )
                        else:
                            # Faculty exists, add new assignments (avoid duplicates)
                            for assignment_data in data['assignments']:
                                FacultyAssignment.objects.get_or_create(
                                    faculty=faculty,
                                    program=assignment_data['program'],
                                    year_section=assignment_data['year_section'],
                                    semester=assignment_data['semester']
                                )
                                
                except Exception as e:
                    errors.append(f'Faculty {faculty_id}: {str(e)}')
                    error_count += 1
                    continue
            
            # Show results
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} faculty members from {file_extension.upper()} file.')
            
            if error_count > 0:
                error_message = f'{error_count} rows had errors:\n' + '\n'.join(errors[:10])
                if len(errors) > 10:
                    error_message += f'\n... and {len(errors) - 10} more errors.'
                messages.error(request, error_message)
                
        except Exception as e:
            messages.error(request, f'Error processing {file_extension.upper()} file: {str(e)}')
    
    return redirect('FacultyList')

@superadmin_required
def download_faculty_csv_template(request):
    """Download a CSV template for faculty import with multiple assignments"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="faculty_import_template.csv"'
    
    writer = csv.writer(response)
    # Write CSV header
    writer.writerow([
        'Faculty ID',
        'First Name', 
        'Last Name',
        'Middle Initial',
        'Program',
        'Year Section',
        'Semester'
    ])
    
    # Add sample data showing multiple assignments for same faculty
    sample_data = [
        ['F2024001', 'John', 'Doe', 'A.', 'Computer Science', '1A', '1st Semester'],
        ['F2024001', '', '', '', 'Computer Science', '2A', '1st Semester'],
        ['F2024001', '', '', '', 'Information Technology', '1B', '2nd Semester'],
        ['F2024002', 'Jane', 'Smith', 'B.', 'Information Technology', '3A', '1st Semester'],
        ['F2024002', '', '', '', 'Information Technology', '4A', '2nd Semester']
    ]
    
    for row in sample_data:
        writer.writerow(row)
    
    return response

@superadmin_required
def download_faculty_excel_template(request):
    """Download an Excel template for faculty import with multiple assignments"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    
    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Faculty Template"
    
    # Define headers
    headers = [
        'Faculty ID',
        'First Name', 
        'Last Name',
        'Middle Initial',
        'Program',
        'Year Section',
        'Semester'
    ]
    
    # Style for headers
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    # Add headers with styling
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
    
    # Add sample data showing multiple assignments
    sample_data = [
        ['F2024001', 'John', 'Doe', 'A.', 'Computer Science', '1A', '1st Semester'],
        ['F2024001', '', '', '', 'Computer Science', '2A', '1st Semester'],
        ['F2024001', '', '', '', 'Information Technology', '1B', '2nd Semester'],
        ['F2024002', 'Jane', 'Smith', 'B.', 'Information Technology', '3A', '1st Semester'],
        ['F2024002', '', '', '', 'Information Technology', '4A', '2nd Semester']
    ]
    
    for row_idx, row_data in enumerate(sample_data, 2):
        for col, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col, value=value)
            cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Add instructions in a separate sheet
    instructions_ws = wb.create_sheet("Instructions")
    instructions = [
        ["Faculty Import Instructions", ""],
        ["", ""],
        ["Required Columns:", ""],
        ["Faculty ID", "Unique identifier for the faculty member (Required)"],
        ["First Name", "Faculty member's first name (Required for first row of each faculty)"],
        ["Last Name", "Faculty member's last name (Required for first row of each faculty)"],
        ["Middle Initial", "Faculty member's middle initial (Optional)"],
        ["Program", "Must be 'Computer Science' or 'Information Technology' (Required for assignments)"],
        ["Year Section", "Year and section (e.g., '1A', '2B') (Required for assignments)"],
        ["Semester", "Semester (e.g., '1st Semester', '2nd Semester') (Required for assignments)"],
        ["", ""],
        ["Multiple Assignments:", ""],
        ["• Each faculty can have multiple program assignments", ""],
        ["• Use the same Faculty ID for multiple rows", ""],
        ["• Only fill First Name, Last Name, and Middle Initial in the first row", ""],
        ["• Leave personal info columns empty for additional assignment rows", ""],
        ["• Each assignment row must have Program, Year Section, and Semester", ""],
        ["", ""],
        ["Important Notes:", ""],
        ["• All imported faculty will have the default password 'welcomeadmin'", ""],
        ["• Existing Faculty IDs will have new assignments added", ""],
        ["• Make sure to follow the exact column names as shown in the template", ""],
        ["• Remove the sample data before importing your actual data", ""],
    ]
    
    for row, (instruction, detail) in enumerate(instructions, 1):
        instructions_ws.cell(row=row, column=1, value=instruction)
        instructions_ws.cell(row=row, column=2, value=detail)
        if row == 1:  # Title
            instructions_ws.cell(row=row, column=1).font = Font(bold=True, size=14)
        elif instruction and instruction.endswith(":"):  # Section headers
            instructions_ws.cell(row=row, column=1).font = Font(bold=True)
    
    # Adjust column widths
    for ws_sheet in [ws, instructions_ws]:
        for column in ws_sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_sheet.column_dimensions[column_letter].width = adjusted_width
    
    # Create response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="faculty_import_template.xlsx"'
    
    wb.save(response)
    return response


@superadmin_required
def check_faculty_id(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            faculty_id = data.get('faculty_id', '').strip()
            
            # Check if faculty ID exists in either Faculty or ArchivedFaculty tables
            exists = (
                Faculty.objects.filter(faculty_id=faculty_id).exists() or 
                ArchivedFaculty.objects.filter(faculty_id=faculty_id).exists()
            )
            
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)