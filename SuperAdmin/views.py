from django.shortcuts import render, redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore
from django.http import JsonResponse
from django.templatetags.static import static
from Login.decorators import superadmin_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json






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
        ,"total_students": total_students
        ,"total_faculty": total_faculty
        ,"cs_students": cs_students_count
        ,"it_students": it_students_count
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
        "show_sticky_container": False,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Activities/contents/Superadmin-Activity-List-content.html', context)
    else:
        return render(request, 'Activities/Superadmin-Activity-List.html', context)

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