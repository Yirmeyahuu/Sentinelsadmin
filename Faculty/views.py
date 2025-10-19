from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.templatetags.static import static
from django.views.decorators.http import require_POST
from firebase_admin import firestore   
from django.http import JsonResponse
import json
from Faculty.forms import AddStudentForm
from django.views.decorators.csrf import csrf_exempt
from Login.decorators import faculty_required
from django.core.paginator import Paginator
from django.templatetags.static import static
from Faculty.models import Faculty, FacultyAssignment
from Student.models import Student, PendingStudent, Task, StudentTaskProgress, ArchivedStudent
from django.db.models import Q, Count
from django.db import transaction
from datetime import datetime, timedelta
import calendar as cal
from django.utils import timezone
import pytz

import csv
import io
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password

from django.urls import reverse

# Firestore database instance
from SentinelsProject.firebase_config import db




# This is the Faculty homepage
@faculty_required
def Faculty_home(request):
    # --- PostgreSQL Data Fetching ---
    try:
        # Get faculty_id from session instead of request.user.username
        faculty_id = request.session.get('faculty_id')
        if not faculty_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('sentinels_login')
            
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
        
        # Get active assignments for this faculty
        faculty_assignments = faculty.assignments.filter(is_active=True)
        
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Total students (PostgreSQL)
    total_students = Student.objects.filter(student_status='Registered').count()
    
    # Computer Science students (PostgreSQL) - Updated to use assignments
    cs_students_count = Student.objects.filter(
        student_status='Registered', 
        faculty_assignment__program='Computer Science'
    ).count()
    
    # Information Technology students (PostgreSQL) - Updated to use assignments
    it_students_count = Student.objects.filter(
        student_status='Registered', 
        faculty_assignment__program='Information Technology'
    ).count()

    # --- Quick Lists ---
    # Recently registered students in any of the faculty's assignments
    quick_students = Student.objects.filter(
        faculty_assignment__in=faculty_assignments
    ).order_by('-pk')[:3]
    
    # Recently submitted pending students for any of the faculty's assignments
    quick_pending_students = []
    for assignment in faculty_assignments:
        pending = PendingStudent.objects.filter(
            program=assignment.program,
            year_section=assignment.year_section,
            semester=assignment.semester
        ).order_by('-submitted_at')[:3]
        quick_pending_students.extend(pending)
    
    # Sort and limit to 3 most recent
    quick_pending_students = sorted(quick_pending_students, key=lambda x: x.submitted_at, reverse=True)[:3]

    # --- Task Progress for Charts (from Firebase) ---
    # Initialize counters
    novice_task_counts = [0, 0, 0, 0]
    junior_task_counts = [0, 0, 0, 0, 0, 0]
    senior_task_counts = [0, 0, 0, 0, 0, 0]
    leaderboard_students = []

    # Task maps for each tier
    novice_tasks = [
        "Novice_Task_1(Collect Books)",
        "Novice_Task_2(Collect USB)",
        "Novice_Task_3(QNA)",
        "Novice_Task_4_(Defeat Rootkit)"
    ]

    junior_tasks = [
        "Junior_Task_1(Collect Books)",
        "Junior_Task_2(Caesar's QNA)",
        "Junior_Task_3(Collect USB)",
        "Junior_Task_4(Bellaso's QNA)",
        "Junior_Task_5(QNA)",
        "Junior_Task_6(Defeat Serpentix2)"
    ]

    senior_tasks = [
        "Senior_Task_1(Collect Books)",
        "Senior_Task_2(QNA)",
        "Senior_Task_3(Collect USB)",
        "Senior_Task_4(QNA)",
        "Senior_Task_5(QNA)",
        "Senior_Task_6(Defeat Rootkit2)"
    ]


    # Process each assignment's Firebase data
    for assignment in faculty_assignments:
        # Query Firebase for students in this assignment's section
        students_query = db.collection("Registered_Students") \
            .where("program", "==", assignment.program) \
            .where("year_section", "==", assignment.year_section) \
            .where("semester", "==", assignment.semester) \
            .stream()

        # Process each student's Firebase data
        for doc in students_query:
            student_data = doc.to_dict()
            student_id = student_data.get("student_id", doc.id)
            first_name = student_data.get("first_name", "")
            last_name = student_data.get("last_name", "")
            
            total_points = 0
            
            # Count Novice tier completions
            for i, task_key in enumerate(novice_tasks):
                task_data = student_data.get(task_key)
                if task_data and isinstance(task_data, dict):
                    points = task_data.get("points", 0)
                    if points > 0:  # Task completed
                        novice_task_counts[i] += 1
                        total_points += int(points)
            
            # Count Junior tier completions
            for i, task_key in enumerate(junior_tasks):
                task_data = student_data.get(task_key)
                if task_data and isinstance(task_data, dict):
                    points = task_data.get("points", 0)
                    if points > 0:  # Task completed
                        junior_task_counts[i] += 1
                        total_points += int(points)
            
            # Count Senior tier completions
            for i, task_key in enumerate(senior_tasks):
                task_data = student_data.get(task_key)
                if task_data and isinstance(task_data, dict):
                    points = task_data.get("points", 0)
                    if points > 0:
                        senior_task_counts[i] += 1
                        total_points += int(points)
            
            # Add to leaderboard if student has points (avoid duplicates)
            if total_points > 0:
                existing_student = next((s for s in leaderboard_students if s["student_id"] == student_id), None)
                if existing_student:
                    existing_student["points"] += total_points
                else:
                    leaderboard_students.append({
                        "student_id": student_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "points": total_points,
                    })

    # Sort leaderboard by total points descending
    leaderboard_students = sorted(leaderboard_students, key=lambda x: x["points"], reverse=True)[:10]


    # FIX: Use Philippine timezone instead of system timezone
    philippine_tz = pytz.timezone('Asia/Manila')
    current_date = timezone.now().astimezone(philippine_tz)

    deadlines_doc = db.collection('Activity Deadlines').document(faculty.faculty_id).get()
    activity_deadlines = {}
    almost_due_tasks = []
    
    if deadlines_doc.exists:
        deadlines_data = deadlines_doc.to_dict()
        for key, deadline_data in deadlines_data.items():
            # Parse deadline date and make it timezone-aware
            deadline_date = datetime.strptime(deadline_data['deadline_date'], '%Y-%m-%d')
            # Make it Philippine timezone aware for comparison
            deadline_date = philippine_tz.localize(deadline_date.replace(hour=23, minute=59, second=59))
            
            day = deadline_date.day
            activity_deadlines[day] = {
                'title': deadline_data['title'],
                'tier': deadline_data.get('tier', ''),
                'date_of_deadline': deadline_data['deadline_date'],
                'time_of_deadline': deadline_data['deadline_time'],
            }
            
            # Use Philippine time for comparison
            current_date_only = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            deadline_date_only = deadline_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if current_date_only <= deadline_date_only <= (current_date_only + timedelta(days=7)):
                days_until = (deadline_date_only - current_date_only).days
                color = 'red' if days_until <= 2 else 'yellow' if days_until <= 4 else 'green'
                almost_due_tasks.append({
                    'name': f"{deadline_data['tier']}: {deadline_data['title']}",
                    'color': color,
                    'deadline': deadline_date.strftime('%Y-%m-%d')
                })
    
    almost_due_tasks.sort(key=lambda x: x['deadline'])

    # Calendar generation function (unchanged)
    def generate_calendar_data(year, month, current_day, timezone_obj):
        """Generate calendar data with proper timezone handling"""
        
        # Get the first day of the month and number of days
        first_day_weekday = cal.weekday(year, month, 1)  # 0=Monday, 6=Sunday
        # Convert to calendar format (0=Sunday, 6=Saturday)
        first_day_weekday = (first_day_weekday + 1) % 7
        
        days_in_month = cal.monthrange(year, month)[1]
        
        calendar_data = []
        
        # Add empty cells for days before month starts
        for _ in range(first_day_weekday):
            calendar_data.append({
                'date': '',
                'is_empty': True,
                'today': False,
                'has_deadline': False
            })
        
        # Add all days of the month
        for day in range(1, days_in_month + 1):
            day_data = {
                'date': day,
                'is_empty': False,
                'today': day == current_day,
                'has_deadline': day in activity_deadlines
            }
            
            if day in activity_deadlines:
                day_data.update(activity_deadlines[day])
                
            calendar_data.append(day_data)
        
        return calendar_data

    # Generate calendar using the improved function
    calendar_days = generate_calendar_data(
        current_date.year, 
        current_date.month, 
        current_date.day, 
        philippine_tz
    )

    context = {
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,  # Add this for template use
        "total_students": total_students,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "calendar_days": calendar_days,
        "almost_due_tasks": almost_due_tasks,
        "current_month": current_date.strftime('%B'),
        "current_year": current_date.year,
        "current_month_year": current_date.strftime('%B %Y'),
        "current_day_name": current_date.strftime('%A'), 
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
    

# This is the student list of Faculty
@faculty_required
def student_list(request):
    # Get faculty using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Get active assignments for this faculty
    faculty_assignments = faculty.assignments.filter(is_active=True).annotate(
        student_count=Count('students', filter=Q(students__student_status='Registered'))
    )
    
    if not faculty_assignments.exists():
        context = {
            "students": [],
            "faculty_data": faculty,
            "faculty_assignments": [],
            "search_query": "",
            "status_filter": "all",
            "selected_program": "all",
            "selected_year_section": "all",
            "selected_semester": "all",
            "sections": [],
            "cs_students": 0,
            "it_students": 0,
            "program_total": 0,
            "section_total": 0,
            "active_students_count": 0,
            "inactive_students_count": 0,
        }
        return render(request, 'Students/student-status.html', context)

    # Get filter values from request
    program_filter = request.GET.get('program', 'all')
    year_section_filter = request.GET.get('year_section', 'all')
    
    # Get unique sections from faculty assignments
    sections = faculty_assignments.values_list('year_section', flat=True).distinct()

    # Base query for students
    students_query = Student.objects.filter(
        faculty_assignment__in=faculty_assignments, 
        student_status='Registered'
    )

    # Apply program filter
    if program_filter != 'all':
        students_query = students_query.filter(
            faculty_assignment__program=program_filter
        )

    # Apply year section filter
    if year_section_filter != 'all':
        students_query = students_query.filter(
            faculty_assignment__year_section=year_section_filter
        )

    # Apply search filter if exists
    search_query = request.GET.get('search', '').strip()
    if search_query:
        students_query = students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    # Order results
    students_query = students_query.order_by('last_name', 'first_name')

    # Calculate counts
    cs_students_count = Student.objects.filter(
        student_status='Registered', 
        faculty_assignment__program='Computer Science',
        faculty_assignment__is_active=True
    ).count()
    
    it_students_count = Student.objects.filter(
        student_status='Registered', 
        faculty_assignment__program='Information Technology',
        faculty_assignment__is_active=True
    ).count()

    section_total = students_query.count()
    program_total = Student.objects.filter(
        faculty_assignment__in=faculty_assignments,
        student_status='Registered'
    ).count()
    total_users = Student.objects.filter(student_status='Registered').count()

    # --- Active/Inactive Students Logic (Firebase) ---
    # Define all task fields to check for activity
    task_fields = [
        # Novice Tasks
        "Novice_Task_1(Collect Books)",
        "Novice_Task_2(Collect USB)",
        "Novice_Task_3(QNA)",
        "Novice_Task_4_(Defeat Rootkit)",
        # Junior Tasks
        "Junior_Task_1(Collect Books)",
        "Junior_Task_2(Caesar's QNA)",
        "Junior_Task_3(Collect USB)", 
        "Junior_Task_4(Bellaso's QNA)",
        "Junior_Task_5(QNA)",
        "Junior_Task_6(Defeat Serpentix2)",
        # Senior Tasks
        "Senior_Task_1(Collect Books)",
        "Senior_Task_2(QNA)",
        "Senior_Task_3(Collect USB)",
        "Senior_Task_4(QNA)",
        "Senior_Task_5(QNA)",
        "Senior_Task_6(Defeat Rootkit2)"
    ]

    active_students_count = 0
    inactive_students_count = 0

    # Get all student IDs from the current query
    student_ids = list(students_query.values_list('student_id', flat=True))

    # Check Firebase for each student's activity
    for student_id in student_ids:
        try:
            # Get student document from Firebase
            doc_ref = db.collection('Registered_Students').document(student_id).get()
            
            if doc_ref.exists:
                student_data = doc_ref.to_dict()
                has_tasks = False
                
                # Check if any task field exists in the student's document
                for task_field in task_fields:
                    if task_field in student_data:
                        has_tasks = True
                        break
                
                if has_tasks:
                    active_students_count += 1
                else:
                    inactive_students_count += 1
            else:
                # Student not found in Firebase = inactive
                inactive_students_count += 1
                
        except Exception as e:
            # If there's an error accessing Firebase, consider student inactive
            print(f"Error checking Firebase for student {student_id}: {e}")
            inactive_students_count += 1

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(students_query, 10) # 5 students per page
    page_obj = paginator.get_page(page_number)


    context = {
        "students": page_obj,
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,
        "total_users": total_users,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "program_total": program_total,
        "section_total": section_total,
        "search_query": search_query,
        "page_obj": page_obj,
        "paginator": paginator,
        "active_students_count": active_students_count,
        "inactive_students_count": inactive_students_count,
        "program_filter": program_filter,
        "year_section_filter": year_section_filter,
        "sections": sections,
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Students/contents/student-list-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Students/student-list.html', context)
    
# This is the student progress of Faculty
@faculty_required
def student_progress(request):
    # Get the logged-in faculty member using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Get active assignments for this faculty
    faculty_assignments = faculty.assignments.filter(is_active=True)
    
    if not faculty_assignments.exists():
        messages.warning(request, "No active assignments found for your account.")
        context = {
            "faculty_data": faculty,
            "faculty_assignments": [],
            "section_total": 0,
            "program_total": 0,
            "novice_count": 0,
            "junior_count": 0,
            "senior_count": 0,
            "active_students_count": 0,
            "inactive_students_count": 0,
        }
        if request.headers.get('HX-Request'):
            return render(request, 'Students/contents/students-progress-content.html', context)
        else:
            return render(request, 'Students/students-progress.html', context)

    # --- Sync Logic: Tier Completion Model ---

    # 1. Get all tasks from DB and group them by tier
    tasks_by_tier = {}
    all_tasks = Task.objects.all()
    for task in all_tasks:
        if task.tier not in tasks_by_tier:
            tasks_by_tier[task.tier] = []
        tasks_by_tier[task.tier].append(task)

    # 2. Get all students for this faculty's assignments
    students_in_section = Student.objects.filter(
        faculty_assignment__in=faculty_assignments, 
        student_status='Registered'
    )

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

    # --- Active/Inactive Students Logic (Firebase) ---
    # Define all task fields to check for activity
    task_fields = [
        # Novice Tasks
        "Novice_Task_1(Collect Books)",
        "Novice_Task_2(Collect USB)",
        "Novice_Task_3(QNA)",
        "Novice_Task_4_(Defeat Rootkit)",
        # Junior Tasks
        "Junior_Task_1(Collect Books)",
        "Junior_Task_2(Caesar's QNA)",
        "Junior_Task_3(Collect USB)", 
        "Junior_Task_4(Bellaso's QNA)",
        "Junior_Task_5(QNA)",
        "Junior_Task_6(Defeat Serpentix2)",
        # Senior Tasks
        "Senior_Task_1(Collect Books)",
        "Senior_Task_2(QNA)",
        "Senior_Task_3(Collect USB)",
        "Senior_Task_4(QNA)",
        "Senior_Task_5(QNA)",
        "Senior_Task_6(Defeat Rootkit2)"
    ]

    active_students_count = 0
    inactive_students_count = 0

    # Get all student IDs from the current query
    student_ids = list(students_in_section.values_list('student_id', flat=True))

    # Check Firebase for each student's activity
    for student_id in student_ids:
        try:
            # Get student document from Firebase
            doc_ref = db.collection('Registered_Students').document(student_id).get()
            
            if doc_ref.exists:
                student_data = doc_ref.to_dict()
                has_tasks = False
                
                # Check if any task field exists in the student's document
                for task_field in task_fields:
                    if task_field in student_data:
                        has_tasks = True
                        break
                
                if has_tasks:
                    active_students_count += 1
                else:
                    inactive_students_count += 1
            else:
                # Student not found in Firebase = inactive
                inactive_students_count += 1
                
        except Exception as e:
            # If there's an error accessing Firebase, consider student inactive
            print(f"Error checking Firebase for student {student_id}: {e}")
            inactive_students_count += 1
    

    # --- Final Counts from PostgreSQL ---
    
    novice_completed_count = Student.objects.filter(
        faculty_assignment__in=faculty_assignments, 
        progress_records__task__tier='Novice'
    ).distinct().count()

    junior_completed_count = Student.objects.filter(
        faculty_assignment__in=faculty_assignments, 
        progress_records__task__tier='Junior'
    ).distinct().count()

    senior_completed_count = Student.objects.filter(
        faculty_assignment__in=faculty_assignments, 
        progress_records__task__tier='Senior'
    ).distinct().count()
    
    # Calculate totals for dashboard cards
    program_total = Student.objects.filter(
        faculty_assignment__in=faculty_assignments,
        student_status='Registered'
    ).count()

    # Calculate overall completion metrics (existing code)
    total_students = program_total if program_total > 0 else 1  # Avoid division by zero
    total_possible_completions = total_students * 3  # 3 tiers per student
    total_completions = novice_completed_count + junior_completed_count + senior_completed_count
    
    # Calculate individual tier completion rates
    novice_completion_rate = format((novice_completed_count / total_students * 100), '.1f')
    junior_completion_rate = format((junior_completed_count / total_students * 100), '.1f')
    senior_completion_rate = format((senior_completed_count / total_students * 100), '.1f')
    
    # Find top tier based on highest completion count (existing code)
    tier_counts = {
        'Novice': 0,
        'Junior': 0,
        'Senior': 0
    }

    # Get the highest tier and the student who achieved it
    top_tier_student = {
        'name': '-',
        'tier': '-'
    }

    # Query Firestore for all students under this faculty's assignments
    for assignment in faculty_assignments:
        students_ref = db.collection('Registered_Students')\
            .where('program', '==', assignment.program)\
            .where('year_section', '==', assignment.year_section)\
            .where('semester', '==', assignment.semester)\
            .stream()

        # Priority order of tiers (highest to lowest)
        tier_priority = ['Senior', 'Junior', 'Novice']

        for student in students_ref:
            student_data = student.to_dict()
            student_name = f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}"
            
            # Check each tier's completion
            for tier in tier_priority:
                if student_data.get(f'{tier}_isComplete', False):
                    tier_counts[tier] += 1
                    # Update top student if this is a higher tier
                    if top_tier_student['tier'] == '-' or \
                       tier_priority.index(tier) < tier_priority.index(top_tier_student['tier']):
                        top_tier_student = {
                            'name': student_name,
                            'tier': tier
                        }
                    break  # Only count highest completed tier per student

    # Get the top tier based on completion counts
    top_tier = max(tier_counts.items(), key=lambda x: x[1])[0] if any(tier_counts.values()) else '-'
    
    # Calculate average completion percentage (existing code)
    average_completion = (total_completions / total_possible_completions * 100) if total_possible_completions > 0 else 0

    # Get current time in Philippine timezone
    philippine_tz = pytz.timezone('Asia/Manila')
    current_time = timezone.now().astimezone(philippine_tz)
    
    # Format the last update time
    last_update = current_time.strftime('%Y-%m-%d %H:%M:%S')

    context = {
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,
        "section_total": students_in_section.count(),
        "program_total": program_total,
        "last_update": last_update,
        "average_completion": f"{average_completion:.1f}",
        "novice_completion_rate": novice_completion_rate,
        "junior_completion_rate": junior_completion_rate,
        "senior_completion_rate": senior_completion_rate,
        "top_tier": top_tier,
        'top_tier_student': top_tier_student,
        "novice_count": novice_completed_count,
        "junior_count": junior_completed_count,
        "senior_count": senior_completed_count,
        "active_students_count": active_students_count,
        "inactive_students_count": inactive_students_count,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/students-progress-content.html', context)
    else:
        return render(request, 'Students/students-progress.html', context)
    

# This is the add student process of Faculty
@faculty_required
def add_student(request):
    print(f"=== ADD STUDENT VIEW CALLED ===")
    print(f"Method: {request.method}")
    print(f"POST data: {request.POST}")
    
    if request.method == "POST":
        # Get faculty from session
        faculty_id = request.session.get('faculty_id')
        if not faculty_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('sentinels_login')
        
        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id)
            print(f"Faculty found: {faculty.faculty_id}")
        except Faculty.DoesNotExist:
            messages.error(request, "Faculty profile not found.")
            return redirect('faculty-student-list')

        form = AddStudentForm(request.POST, faculty=faculty)
        
        if form.is_valid():
            print("Form is valid")
            try:
                # Use atomic transaction to ensure both PostgreSQL and Firestore succeed or fail together
                with transaction.atomic():
                    student = form.save()
                    print(f"Student saved to PostgreSQL: {student.student_id}")
                    
                    # Create Firestore record
                    firestore_data = {
                        'student_id': student.student_id,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'middle_initial': student.middle_initial,
                        'program': student.faculty_assignment.program,
                        'year_section': student.faculty_assignment.year_section,
                        'semester': student.faculty_assignment.semester,
                    }
                    
                    try:
                        db.collection('Registered_Students').document(student.student_id).set(firestore_data)
                        print(f"Firestore record created for {student.student_id}")
                    except Exception as firestore_error:
                        print(f"Firestore error: {firestore_error}")
                        # Re-raise to trigger transaction rollback
                        raise firestore_error
                    
                messages.success(request, f"Student {student.student_id} added successfully!")
                print("Student addition completed successfully")
                
            except Exception as e:
                messages.error(request, f"Error adding student: {str(e)}")
                print(f"Error during save: {str(e)}")
                
            return redirect('faculty-student-list')
        else:
            print(f"Form errors: {form.errors}")
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('faculty-student-list')
    else:
        print("Not a POST request, redirecting")
        return redirect('faculty-student-list')


# Add check student ID endpoint
@faculty_required
def check_student_id(request):
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id', '')
            exists = Student.objects.filter(student_id=student_id).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'exists': False, 'error': str(e)})
    return JsonResponse({'exists': False})


# This is the edit student process of Faculty
@faculty_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                new_student_id = request.POST.get("student_id")
                
                # If student ID is changing 
                if new_student_id != student_id:
                    # Check if new ID is available
                    if Student.objects.filter(student_id=new_student_id).exists():
                        messages.error(request, "Student ID is already taken.")
                        return redirect("faculty-student-list")
                    
                    try:
                        # Update Firestore first
                        firestore_data = {
                            'student_id': new_student_id,
                            'first_name': request.POST.get("first_name", student.first_name),
                            'last_name': request.POST.get("last_name", student.last_name),
                            'middle_initial': request.POST.get("middle_initial", student.middle_initial),
                            'program': student.faculty_assignment.program,
                            'year_section': student.faculty_assignment.year_section,
                            'semester': student.faculty_assignment.semester,
                        }
                        
                        # Delete old document and create new one
                        old_doc = db.collection('Registered_Students').document(student_id)
                        new_doc = db.collection('Registered_Students').document(new_student_id)
                        
                        new_doc.set(firestore_data)
                        old_doc.delete()
                        
                        # Now update PostgreSQL
                        # Update all fields in a single operation using filter and update
                        Student.objects.filter(student_id=student_id).update(
                            student_id=new_student_id,
                            first_name=request.POST.get("first_name", student.first_name),
                            last_name=request.POST.get("last_name", student.last_name),
                            middle_initial=request.POST.get("middle_initial", student.middle_initial),
                            faculty_assignment_id=request.POST.get("faculty_assignment_id", student.faculty_assignment_id)
                        )
                        
                    except Exception as e:
                        raise Exception(f"Update failed: {str(e)}")
                
                else:
                    # Regular update without ID change
                    Student.objects.filter(student_id=student_id).update(
                        first_name=request.POST.get("first_name", student.first_name),
                        last_name=request.POST.get("last_name", student.last_name),
                        middle_initial=request.POST.get("middle_initial", student.middle_initial),
                        faculty_assignment_id=request.POST.get("faculty_assignment_id", student.faculty_assignment_id)
                    )
                    
                    # Update Firestore
                    firestore_data = {
                        'first_name': request.POST.get("first_name", student.first_name),
                        'last_name': request.POST.get("last_name", student.last_name),
                        'middle_initial': request.POST.get("middle_initial", student.middle_initial),
                        'program': student.faculty_assignment.program,
                        'year_section': student.faculty_assignment.year_section,
                        'semester': student.faculty_assignment.semester,
                    }
                    db.collection('Registered_Students').document(student_id).update(firestore_data)

                messages.success(request, "Student details updated successfully!")
                
        except Exception as e:
            messages.error(request, f"Error updating student: {str(e)}")
            return redirect("faculty-student-list")
            
    return redirect("faculty-student-list")


# This is the archived students list of Faculty
@faculty_required
def archived_students_list_page(request):
    """
    Displays a list of students archived by the currently logged-in faculty.
    Handles search and HTMX requests with pagination.
    """
    # Get faculty using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')

    # Get the Faculty profile
    try:
        faculty = Faculty.objects.get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Base queryset for archived students belonging to this faculty
    archived_students_query = ArchivedStudent.objects.filter(faculty=faculty)

    # Handle search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        archived_students_query = archived_students_query.filter(
            Q(student_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(program__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(archived_students_query.order_by('-archived_at'), 10)  # 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "archived_students": page_obj,
        "faculty_data": faculty,
        "search_query": search_query,
        "paginator": paginator,
        "page_obj": page_obj,
    }

    # Handle HTMX requests for partial page updates
    if request.headers.get('HX-Request'):
        return render(request, "Students/contents/students-archived-content.html", context)
    
    # Handle standard requests for a full page load
    return render(request, "Students/students-archived.html", context)

# This is the verify student process of Faculty
@faculty_required
def Verify_Student(request):
    # Get the logged-in faculty member using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Get active assignments for this faculty
    faculty_assignments = faculty.assignments.filter(is_active=True)
    
    if not faculty_assignments.exists():
        messages.warning(request, "No active assignments found for your account.")
        context = {
            "faculty_data": faculty,
            "verify_students": [],
            "search_query": "",
        }
        if request.headers.get('HX-Request'):
            return render(request, 'Students/contents/students-verify-list-content.html', context)
        else:
            return render(request, 'Students/students-verify-list.html', context)
    
    # Build query for pending students that match ANY of the faculty's active assignments
    assignment_filters = Q()
    for assignment in faculty_assignments:
        assignment_filters |= Q(
            program=assignment.program,
            year_section=assignment.year_section,
            semester=assignment.semester
        )
    
    # Filter pending students that match the faculty's class assignments
    pending_students_query = PendingStudent.objects.filter(
        assignment_filters
    ).order_by('submitted_at')

    # Apply search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        pending_students_query = pending_students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(program__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(pending_students_query, 10)  # 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,
        "verify_students": page_obj,
        "search_query": search_query,
        "paginator": paginator,
        "page_obj": page_obj,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/students-verify-list-content.html', context)
    else:
        return render(request, 'Students/students-verify-list.html', context)
    
# This is the faculty activity page
@faculty_required
def Faculty_activity_page(request):
    # Get faculty data from PostgreSQL using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
        
        # Get active assignments for this faculty
        assignments = faculty.assignments.filter(is_active=True)
        
        faculty_data = {
            "faculty_id": faculty.faculty_id,
            "first_name": faculty.first_name,
            "last_name": faculty.last_name,
            "middle_initial": faculty.middle_initial,
            "assignments": assignments,  # Pass assignments instead of individual fields
        }
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    activities_novice = [
        {
            "title": "Novice Task 1",
            "description": "In this quest, the player begins their journey at CyberTech Academy, guided by their instructor, Katrina Salazar, who assigns their first task: researching the meaning of cybersecurity. As the player explores the library, a memory of their late father—a legendary cybersecurity expert—resurfaces, emphasizing the importance of understanding the people behind the systems. The quest unfolds through interactive NPC encounters, where the player answers questions to define cybersecurity, identify key career paths such as Security Architect and Ethical Hacker, and understand the anatomy of a cyber attack. Each correct response unlocks achievements and advances the story, immersing the player in a hands-on introduction to the world of cybersecurity.",
            "image": static("assets/tier-thumbnail/novice-thumbnail.webp"),
        },
        {
            "title": "Novice Task 2",
            "description": "In this second quest, the player continues their training at CyberTech Academy, diving deeper into the realities of cybersecurity threats and vulnerabilities. A vivid flashback recalls a stormy night when the player's father swiftly neutralized a cyber threat, warning that the key to defense lies in identifying weak spots before attackers do. Now seated in the computer lab, the player begins researching risks that organizations face. Through a sequence of NPC-guided tasks, they must correctly identify internal threats like employees, recognize cybersecurity vulnerabilities such as card skimmers, and demonstrate understanding of core principles like the CIA Triad—particularly how confidentiality relies on encryption and hashing. Each correct answer grants achievements and brings the player closer to mastering the fundamentals of digital defense.",
            "image": static("assets/tier-thumbnail/novice-thumbnail.webp"),
        },
        {
            "title": "Novice Task 3",
            "description": "In the third and final quest, the player is challenged to apply their growing knowledge of cybersecurity to real-world frameworks and strategies. A flashback to a simple but powerful lesson from their father—People, Processes, Technology—sets the stage for what lies ahead. Tasked with interviewing the right faculty members, the player must navigate the faculty office, identifying which professors hold the expertise needed to discuss security tactics, emerging technologies, and types of cybersecurity. Choosing the wrong person leads to rejection, while finding the right expert unlocks valuable insights. Returning to the classroom, the player answers reflection questions based on their interviews. With each correct response and interaction, achievements are earned, bringing them one step closer to becoming a well-rounded digital defender, just like their father envisioned.",
            "image": static("assets/tier-thumbnail/novice-thumbnail.webp"),
        },
        {
            "title": "Novice Boss Battle",
            "description": "In the Novice Boss Battle, the player faces their first major test as the academy's network is suddenly compromised. The school's AI assistant has been hijacked and transformed into The Deceiver AI, a malicious entity designed to challenge the player's grasp of cybersecurity. As classroom screens fade to black and a chilling robotic voice taunts them, the player recalls their father's warning about social engineering: that deception, not just intrusion, is a hacker's greatest weapon. To stop the AI from spreading misinformation and damaging the academy's defenses, the player must correctly answer three tricky cybersecurity questions that blur the line between truth and lie. Success earns them the Defender of Knowledge achievement, while failure results in data corruption and a forced retry—proving that in cybersecurity, knowing the truth is the first line of defense.",
            "image": static("assets/tier-thumbnail/novice-thumbnail.webp"),
        },
    ]
    
    activities_junior = [
        {
            "title": "Junior Task 1",
            "description": "In Task 1, the player starts their internship in a cybersecurity office and is assigned to research the concept of a domain. A flashback with their father emphasizes the importance of organized systems in network security. The player uses their workstation to investigate and is later questioned by the CISO. If they correctly define a domain as a group of devices managed under the same rules, they are allowed to proceed. A wrong answer sends them back to research before moving to the Incident Response Room to study cryptography.",
            "image": static("assets/tier-thumbnail/junior-thumbnail.webp"),
        },
        {
            "title": "Junior Task 2",
            "description": "In Task 2, the player enters the Incident Response Room to assist an employee named John with a suspicious encrypted email. A flashback from their father highlights the dual nature of encryption—protective but potentially dangerous. After analyzing the email using basic cipher clues, the player must choose the correct response: report the email and isolate the system. A correct choice earns praise and leads to a report to the CISO. The task ends with the player writing a policy to help others recognize phishing attempts.",
            "image": static("assets/tier-thumbnail/junior-thumbnail.webp"),
        },
        {
            "title": "Junior Task 3",
            "description": "In Task 3, the player drafts a company security policy, reminded by their father that people are the strongest defense against cyber threats. They must choose the best policy to protect the company. The correct choice is to train employees to recognize and report phishing emails. Selecting this earns praise for promoting awareness. Wrong answers prompt a reminder that effective policies focus on education, not restrictions or risky behavior.",
            "image": static("assets/tier-thumbnail/junior-thumbnail.webp"),
        },
        {
            "title": "Junior Boss Battle",
            "description": "In the Junior Boss Battle, the player faces a crafty hacker disguised as an employee who uses social engineering tactics to steal data. The player must spot fake emails, false boss impersonations, and phishing login pages before time expires. Falling for any trick means restarting the fight. Success rewards the Master of Awareness achievement. A flashback reminds the player that the biggest threats often come disguised as harmless.",
            "image": static("assets/tier-thumbnail/junior-thumbnail.webp"),
        },
    ]
    
    activities_senior = [
        {
            "title": "Senior Task 1",
            "description": "Threat Landscape, the player is called to the Cyber Threat Intelligence Lab to analyze the company's network for vulnerabilities. Guided by a flashback of their father's advice, they must identify weak points before attackers do. The key challenge is recognizing that weak passwords on wireless access points are a major risk. Correct answers lead to praise and progression; wrong answers require retrying the analysis. This task emphasizes the importance of spotting real network threats early.",
            "image": static("assets/tier-thumbnail/senior-thumbnail.webp"),
        },
        {
            "title": "Senior Task 2",
            "description": "Ontology of Malware, the player analyzes a malware report on the Malware Analysis Workstation to classify a new threat. Guided by a flashback from their father, they learn that malware can be deceptive as well as destructive. The player must identify ransomware—a type that encrypts files and demands payment—based on its behavior. Correct identification earns praise and progression; mistakes require retrying the classification. This task highlights the importance of recognizing malware types for effective cybersecurity responses.",
            "image": static("assets/tier-thumbnail/senior-thumbnail.webp"),
        },
        {
            "title": "Senior Task 3",
            "description": "Risk Management & Incident Countermeasure, the player leads a simulated breach response after an alert shows unauthorized access and data theft. A flashback reminds them that quick action is crucial during an attack. The player must choose the best first steps—disconnecting the compromised system and blocking the attacker's IP—to contain the threat. Correct choices earn praise and progress, while wrong ones prompt a retry. This task emphasizes swift and effective incident response in cybersecurity.",
            "image": static("assets/tier-thumbnail/senior-thumbnail.webp"),
        },
        {
            "title": "Senior Boss Battle",
            "description": "The player now faces an advanced AI-powered malware that adapts to every defense they deploy. The virus launches attacks like DDoS, ransomware, and privilege escalation, and the player must quickly select the correct countermeasure to stop each one. Acting too slowly or choosing wrong lets the virus mutate, making it harder to defeat. Success earns the Cyber Guardian achievement. A flashback reminds the player: threats evolve fast, so staying sharp and acting swiftly is key.",
            "image": static("assets/tier-thumbnail/senior-thumbnail.webp"),
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
    
    # Get activity deadlines from Firestore - Use faculty_id directly
    deadlines_doc = db.collection('Activity Deadlines').document(faculty_id).get()
    activity_deadlines = {}
    
    if deadlines_doc.exists:
        deadlines_data = deadlines_doc.to_dict()
        # Map Firebase tasks to display titles
        task_to_display = {
            "Junior_Task_1(Collect Books)": "Junior Task 1",
            "Junior_Task_2(Caesar's QNA)": "Junior Task 1",
            "Junior_Task_3(Collect USB)": "Junior Task 2",
            "Junior_Task_4(Bellaso's QNA)": "Junior Task 2",
            "Junior_Task_5(QNA)": "Junior Task 3",
            "Junior_Task_6(Defeat Serpentix2)": "Junior Boss Battle",
            "Senior_Task_1(Collect Books)": "Senior Task 1",
            "Senior_Task_2(QNA)": "Senior Task 1",
            "Senior_Task_3(Collect USB)": "Senior Task 2",
            "Senior_Task_4(QNA)": "Senior Task 2",
            "Senior_Task_5(QNA)": "Senior Task 3",
            "Senior_Task_6(Defeat Rootkit2)": "Senior Boss Battle"
        }
        
        # Process each deadline entry
        for key, deadline_data in deadlines_data.items():
            if isinstance(deadline_data, dict):
                display_title = task_to_display.get(key) or deadline_data.get('display_title')
                if display_title:
                    # Use the first deadline found for combined tasks
                    if display_title not in activity_deadlines:
                        activity_deadlines[display_title] = {
                            'deadline_date': deadline_data.get('deadline_date'),
                            'deadline_time': deadline_data.get('deadline_time')
                        }
    
    # Add isLock and deadline info to each activity (update this section)
    for activity in activities_novice:
        activity['isLock'] = lock_states.get('Novice', True)
        deadline_info = activity_deadlines.get(activity['title'], {})
        activity['deadline_date'] = deadline_info.get('deadline_date')
        activity['deadline_time'] = deadline_info.get('deadline_time')
        activity['progress'] = 0
        
    for activity in activities_junior:
        activity['isLock'] = lock_states.get('Junior', True)
        deadline_info = activity_deadlines.get(activity['title'], {})
        activity['deadline_date'] = deadline_info.get('deadline_date')
        activity['deadline_time'] = deadline_info.get('deadline_time')
        activity['progress'] = 0
        activity['subject'] = 'Cybersecurity'
        
    for activity in activities_senior:
        activity['isLock'] = lock_states.get('Senior', True)
        deadline_info = activity_deadlines.get(activity['title'], {})
        activity['deadline_date'] = deadline_info.get('deadline_date')
        activity['deadline_time'] = deadline_info.get('deadline_time')
        activity['progress'] = 0
        activity['subject'] = 'Advanced Cybersecurity'

    context = {
        "faculty_data": faculty_data,
        "activities_novice": activities_novice,
        "activities_junior": activities_junior,
        "activities_senior": activities_senior,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Activities/contents/Faculty-Activity-List-content.html', context)
    else:
        return render(request, 'Activities/Faculty-Activity-List.html', context)
    
@faculty_required
def accept_student(request, student_id):
    # Get faculty using session instead of request.user.username
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
        
    faculty = get_object_or_404(Faculty, faculty_id=faculty_id)
    pending_student = get_object_or_404(PendingStudent, student_id=student_id)

    try:
        # Find the appropriate faculty assignment for this student
        faculty_assignment = FacultyAssignment.objects.filter(
            faculty=faculty,
            program=pending_student.program,
            year_section=pending_student.year_section,
            semester=pending_student.semester,
            is_active=True
        ).first()
        
        if not faculty_assignment:
            messages.error(request, "No matching active assignment found for this student's program and section.")
            return redirect('verify-students')

        # Create the student in PostgreSQL with faculty_assignment
        new_student = Student.objects.create(
            student_id=pending_student.student_id,
            first_name=pending_student.first_name,
            last_name=pending_student.last_name,
            middle_initial=pending_student.middle_initial,
            faculty_assignment=faculty_assignment,  # Use faculty_assignment instead of faculty
            student_status='Registered',
            password=pending_student.password
        )

        # Prepare the data for Firestore from the pending student object
        firestore_data = {
            'student_id': pending_student.student_id,
            'first_name': pending_student.first_name,
            'last_name': pending_student.last_name,
            'middle_initial': pending_student.middle_initial,
            'program': pending_student.program,
            'year_section': pending_student.year_section,
            'semester': pending_student.semester,
        }

        # Create the corresponding document in Firestore with student details
        try:
            db.collection('Registered_Students').document(new_student.student_id).set(firestore_data)
        except Exception as e:
            messages.error(request, f"Student accepted, but failed to create Firestore record: {e}")

        # Delete the pending record from PostgreSQL
        pending_student.delete()
        
        messages.success(request, f"Student {new_student.first_name} {new_student.last_name} has been accepted.")
    except Exception as e:
        messages.error(request, f"An error occurred while accepting the student: {e}")

    return redirect('verify-students')


# This is the reject student process of Faculty
@faculty_required
def reject_student(request, student_id):
    pending_student = get_object_or_404(PendingStudent, student_id=student_id)
    try:
        pending_student.delete()
        messages.success(request, f"Registration for student {pending_student.first_name} {pending_student.last_name} has been rejected.")
    except Exception as e:
        messages.error(request, f"An error occurred while rejecting the student: {e}")

    return redirect('verify-students')



# This is the faculty account page
@faculty_required
def faculty_account(request):
    faculty_id = request.session.get('faculty_id')  # Use session instead of request.user.username
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty_obj = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
        
        # Get active assignments for this faculty
        assignments = faculty_obj.assignments.filter(is_active=True)
        
        faculty_data = {
            "faculty_id": faculty_obj.faculty_id,
            "first_name": faculty_obj.first_name,
            "last_name": faculty_obj.last_name,
            "middle_initial": faculty_obj.middle_initial,
            "assignments": assignments,  # Pass assignments instead of individual fields
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
    
# This is the edit faculty account process
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


# This is the upload faculty profile image process
def handle_image_upload(image):
    # Implement your image upload logic
    pass

#This is the move student process of Faculty
@faculty_required
def move_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        destination = request.POST.get("destination")

        collections = [
            "Registered_Students",
            "Completed Students",
            "Drop-out Students",
        ]  # Removed "Archived Students" since it doesn't exist in Firebase
        student = None
        student_data = None
        found_collection = None

        # First, try to find student in Firebase collections
        for collection in collections:
            ref = db.collection(collection).document(student_id)
            doc = ref.get()
            if doc.exists:
                student = ref
                student_data = doc.to_dict()
                found_collection = collection
                break

        # If not found in Firebase, check if it's an archived student being restored
        if not student_data and destination == "registered":
            try:
                archived_student = ArchivedStudent.objects.get(student_id=student_id)
                # Create student_data from archived student for Firebase (WITHOUT password and status)
                student_data = {
                    "student_id": archived_student.student_id,
                    "first_name": archived_student.first_name,
                    "last_name": archived_student.last_name,
                    "middle_initial": archived_student.middle_initial,
                    "program": archived_student.program,
                    "year_section": archived_student.year_section,
                    "semester": archived_student.semester,
                    # Removed: password and status - these belong only in PostgreSQL
                }
                found_collection = "Archive"  # Indicate it came from archive
            except ArchivedStudent.DoesNotExist:
                pass

        if not student_data:
            messages.error(request, "Student not found.")
            return redirect("faculty-student-list")

        # Get faculty using session
        faculty_id = request.session.get('faculty_id')
        if not faculty_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('sentinels_login')
            
        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id)
        except Faculty.DoesNotExist:
            messages.error(request, "Faculty profile not found.")
            return redirect("faculty-student-list")

        if destination == "registered":
            # Move to Registered_Students (Firebase doesn't store status or password)
            db.collection("Registered_Students").document(student_id).set(student_data)
            
            # Remove from old Firebase collection if it exists (but not if from archive)
            if found_collection != "Archive" and found_collection != "Registered_Students" and student:
                student.delete()
            
            # Update PostgreSQL Student status or restore from archive
            try:
                # Check if student exists in ArchivedStudent table
                archived_student = ArchivedStudent.objects.get(student_id=student_id)
                
                # Find the appropriate faculty assignment for restoration
                faculty_assignment = FacultyAssignment.objects.filter(
                    faculty=faculty,
                    program=archived_student.program,
                    year_section=archived_student.year_section,
                    semester=archived_student.semester,
                    is_active=True
                ).first()
                
                if not faculty_assignment:
                    messages.error(request, "No matching active assignment found for this student's program and section.")
                    return redirect("faculty-student-list")
                
                # Restore student from archive to active Student table
                Student.objects.create(
                    student_id=archived_student.student_id,
                    first_name=archived_student.first_name,
                    last_name=archived_student.last_name,
                    middle_initial=archived_student.middle_initial,
                    password=archived_student.password,  # Password only in PostgreSQL
                    faculty_assignment=faculty_assignment,  # Use faculty_assignment instead of faculty
                    student_status='Registered'  # Status only in PostgreSQL
                )
                # Remove from archived table
                archived_student.delete()
                messages.success(request, "Student restored from archive to Registered Students.")
            except ArchivedStudent.DoesNotExist:
                # Student is not in archive, just update status if exists in Student table
                try:
                    Student.objects.filter(student_id=student_id).update(student_status='Registered')
                    messages.success(request, "Student status updated to Registered.")
                except Student.DoesNotExist:
                    messages.success(request, "Student moved to Registered Students.")
                
        elif destination == "completed":
            # Move to Completed Students in Firebase (no status stored)
            db.collection("Completed Students").document(student_id).set(student_data)
            if found_collection != "Completed Students" and student:
                student.delete()
                
            # Update PostgreSQL Student status only
            try:
                Student.objects.filter(student_id=student_id).update(student_status='Completed')
            except Student.DoesNotExist:
                pass
                
            messages.info(request, "Student moved to Completed Students successfully.")
            
        elif destination == "dropout":
            # Move to Drop-out Students in Firebase (no status stored)
            db.collection("Drop-out Students").document(student_id).set(student_data)
            if found_collection != "Drop-out Students" and student:
                student.delete()
                
            # Update PostgreSQL Student status only
            try:
                Student.objects.filter(student_id=student_id).update(student_status='Drop-out')
            except Student.DoesNotExist:
                pass
                
            messages.success(request, "Student moved to Drop-out Students successfully!")
            
        elif destination == "archive":
            try:
                # Get the student from PostgreSQL
                postgres_student = Student.objects.get(student_id=student_id)
                # Get faculty_assignment details
                faculty_assignment = postgres_student.faculty_assignment

                ArchivedStudent.objects.create(
                    student_id=postgres_student.student_id,
                    first_name=postgres_student.first_name,
                    last_name=postgres_student.last_name,
                    middle_initial=postgres_student.middle_initial,
                    password=postgres_student.password,
                    program=faculty_assignment.program if faculty_assignment else '',
                    year_section=faculty_assignment.year_section if faculty_assignment else '',
                    semester=faculty_assignment.semester if faculty_assignment else '',
                    faculty=faculty_assignment.faculty if faculty_assignment else faculty,
                    faculty_assignment=faculty_assignment if faculty_assignment else None,
                )

                postgres_student.delete()

            except Student.DoesNotExist:
                # If student doesn't exist in PostgreSQL, create archived record from Firestore data
                ArchivedStudent.objects.create(
                    student_id=student_id,
                    first_name=student_data.get('first_name', ''),
                    last_name=student_data.get('last_name', ''),
                    middle_initial=student_data.get('middle_initial', ''),
                    password='',  # Empty password - will need reset when restored
                    program=student_data.get('program', ''),
                    year_section=student_data.get('year_section', ''),
                    semester=student_data.get('semester', ''),
                    faculty=faculty,
                )

            # Remove student from Firebase (no "Archived Students" collection needed)
            if found_collection and student:
                student.delete()

            messages.success(request, "Student moved to Archive successfully!")
            
        else:
            messages.error(request, "Invalid destination.")
            return redirect("faculty-student-list")
            
    return redirect(request.META.get('HTTP_REFERER', 'faculty-student-list'))


@faculty_required
@require_POST
def restoreStudent(request):
    student_id = request.POST.get('student_id')
    try:
        with transaction.atomic():
            archived_student = ArchivedStudent.objects.get(student_id=student_id)
            # Find a valid faculty assignment
            faculty_assignment = FacultyAssignment.objects.filter(
                program=archived_student.program,
                year_section=archived_student.year_section,
                semester=archived_student.semester,
                is_active=True
            ).first()
            # Create in PostgreSQL
            student = Student.objects.create(
                student_id=archived_student.student_id,
                first_name=archived_student.first_name,
                last_name=archived_student.last_name,
                middle_initial=archived_student.middle_initial,
                faculty_assignment=faculty_assignment,
                student_status='Registered'
            )
            # Create in Firestore
            firestore_data = {
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'middle_initial': student.middle_initial,
                'program': faculty_assignment.program if faculty_assignment else archived_student.program,
                'year_section': faculty_assignment.year_section if faculty_assignment else archived_student.year_section,
                'semester': faculty_assignment.semester if faculty_assignment else archived_student.semester,
            }
            db.collection('Registered_Students').document(student.student_id).set(firestore_data)
            # Remove from archive
            archived_student.delete()
            messages.success(request, "Student has been restored successfully!")
    except ArchivedStudent.DoesNotExist:
        messages.error(request, "Student not found in archive.")
    except Exception as e:
        messages.error(request, f"Error restoring student: {str(e)}")

    return redirect('archived_students_list')


# This is the novice tier page of Faculty
@faculty_required
def novice_tier(request):
    # Get the logged-in faculty member using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Get active assignments for this faculty
    faculty_assignments = faculty.assignments.filter(is_active=True)
    
    if not faculty_assignments.exists():
        messages.warning(request, "No active assignments found for your account.")
        context = {
            "novice_students": [],
            "novice_leaderboard": [],
            "faculty_data": faculty,
            "faculty_assignments": [],
            "selected_task": "task1",
        }
        return render(request, 'Tier/Novice.html', context)

    # Task map for filtering
    task_map = {
        "task1": "Novice_Task_1(Collect Books)",
        "task2": "Novice_Task_2(Collect USB)",
        "task3": "Novice_Task_3(QNA)",
        "task4": "Novice_Task_4_(Defeat Rootkit)",
    }
    selected_task = request.GET.get("task", "task1")
    selected_task_map = task_map.get(selected_task, "Novice_Task_1(Collect Books)")


    # Get current time in Philippine timezone
    philippine_tz = pytz.timezone('Asia/Manila')
    current_time = timezone.now().astimezone(philippine_tz)
    last_update = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # Get total students for completion rate calculation
    total_students = Student.objects.filter(
        faculty_assignment__in=faculty_assignments,
        student_status='Registered'
    ).count()


    # Calculate task completion metrics
    novice_students = []
    leaderboard_students = []
    completed_tasks = 0
    total_points = 0
    total_completed_tasks = 0  # Add this initialization
    task_completion_stats = {task_id: 0 for task_id in task_map}
    students_with_tasks = set() 
    completed_all_tasks = 0
    students_with_points = set()

    # Process each assignment's Firebase data
    for assignment in faculty_assignments:
        students_query = db.collection("Registered_Students") \
            .where("program", "==", assignment.program) \
            .where("year_section", "==", assignment.year_section) \
            .where("semester", "==", assignment.semester) \
            .stream()

        for doc in students_query:
            student = doc.to_dict()
            student_id = student.get("student_id", doc.id)
            
            # Process individual task data
            student_total_points = 0
            student_completed_tasks = 0
            
            for task_key in task_map.values():
                task_data = student.get(task_key)
                if task_data and isinstance(task_data, dict):
                    points = int(task_data.get("points", 0))
                    if points > 0:
                        student_total_points += points
                        student_completed_tasks += 1
                        total_completed_tasks += 1

            # Add to total points if student has any
            if student_total_points > 0:
                total_points += student_total_points
                students_with_points.add(student_id)

            # Add to leaderboard if has points
            if student_total_points > 0:
                leaderboard_students.append({
                    "student_id": student_id,
                    "first_name": student.get("first_name", ""),
                    "last_name": student.get("last_name", ""),
                    "points": student_total_points,
                    "tasks_completed": student_completed_tasks,
                    "completion_percentage": (student_completed_tasks / len(task_map)) * 100
                })

            # Add to progress table for selected task
            selected_task = request.GET.get("task", "task1")
            selected_task_map = task_map.get(selected_task)
            task_data = student.get(selected_task_map)
            if task_data:
                novice_students.append({
                    "student_id": student_id,
                    "first_name": student.get("first_name", ""),
                    "last_name": student.get("last_name", ""),
                    "points": task_data.get("points", 0),
                    "total_time_completed": task_data.get("time_taken", ""),
                })

    # Calculate stats for cards
    active_students = len(students_with_points)
    average_score = total_points / active_students if active_students > 0 else 0
    completed_tasks_count = total_completed_tasks

    # Sort leaderboard
    novice_leaderboard = sorted(
        leaderboard_students,
        key=lambda x: (-x["points"], -x["tasks_completed"])
    )

    context = {
        "novice_students": novice_students,
        "novice_leaderboard": novice_leaderboard,
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,  # Add assignments to context
        "selected_task": selected_task,
        "total_students": total_students,
        "completed_tasks_count": completed_tasks_count,
        "average_score": average_score,
        "last_update": last_update,
        "task_map": task_map,
    }
    return render(request, 'Tier/Novice.html', context) 


# This is the junior tier page of Faculty
@faculty_required
def junior_tier(request):
    # Get the logged-in faculty member using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Get active assignments for this faculty
    faculty_assignments = faculty.assignments.filter(is_active=True)
    
    if not faculty_assignments.exists():
        messages.warning(request, "No active assignments found for your account.")
        context = {
            "junior_students": [],
            "junior_leaderboard": [],
            "faculty_data": faculty,
            "faculty_assignments": [],
            "selected_task": "task1",
        }
        return render(request, 'Tier/Junior.html', context)

    # Task map for filtering Junior tier tasks
    task_map = {
        "task1": "Junior_Task_1(Collect Books)",
        "task2": "Junior_Task_2(Caesar's QNA)",
        "task3": "Junior_Task_3(Collect USB)",
        "task4": "Junior_Task_4(Bellaso's QNA)",
        "task5": "Junior_Task_5(QNA)",
        "task6": "Junior_Task_6(Defeat Serpentix2)",
    }

    selected_task = request.GET.get("task", "task1")
    
    # Get current time in Philippine timezone
    philippine_tz = pytz.timezone('Asia/Manila')
    current_time = timezone.now().astimezone(philippine_tz)
    last_update = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # Get total students for completion rate calculation
    total_students = Student.objects.filter(
        faculty_assignment__in=faculty_assignments,
        student_status='Registered'
    ).count()

    # Initialize tracking variables
    junior_students = []
    leaderboard_students = []
    completed_tasks = 0
    total_points = 0
    total_completed_tasks = 0
    task_completion_stats = {task_id: 0 for task_id in task_map}
    students_with_tasks = set()
    students_with_points = set()

    # Process Firebase data
    for assignment in faculty_assignments:
        students_query = db.collection("Registered_Students") \
            .where("program", "==", assignment.program) \
            .where("year_section", "==", assignment.year_section) \
            .where("semester", "==", assignment.semester) \
            .stream()

        for doc in students_query:
            student = doc.to_dict()
            student_id = student.get("student_id", doc.id)
            
            # Process individual task data
            student_total_points = 0
            student_completed_tasks = 0
            
            for task_key in task_map.values():
                task_data = student.get(task_key)
                if task_data and isinstance(task_data, dict):
                    points = int(task_data.get("points", 0))
                    if points > 0:
                        student_total_points += points
                        student_completed_tasks += 1
                        total_completed_tasks += 1

            # Add to total points if student has any
            if student_total_points > 0:
                total_points += student_total_points
                students_with_points.add(student_id)

            # Add to leaderboard if has points
            if student_total_points > 0:
                leaderboard_students.append({
                    "student_id": student_id,
                    "first_name": student.get("first_name", ""),
                    "last_name": student.get("last_name", ""),
                    "points": student_total_points,
                    "tasks_completed": student_completed_tasks,
                    "completion_percentage": (student_completed_tasks / len(task_map)) * 100
                })

            # Add to progress table for selected task
            selected_task = request.GET.get("task", "task1")
            selected_task_map = task_map.get(selected_task)
            task_data = student.get(selected_task_map)
            if task_data:
                junior_students.append({
                    "student_id": student_id,
                    "first_name": student.get("first_name", ""),
                    "last_name": student.get("last_name", ""),
                    "points": task_data.get("points", 0),
                    "total_time_completed": task_data.get("time_taken", ""),
                })

    # Calculate stats for cards
    active_students = len(students_with_points)
    average_score = total_points / active_students if active_students > 0 else 0
    completed_tasks_count = total_completed_tasks

    # Sort leaderboard
    junior_leaderboard = sorted(
        leaderboard_students,
        key=lambda x: (-x["points"], -x["tasks_completed"])
    )

    context = {
        "junior_students": junior_students,
        "junior_leaderboard": junior_leaderboard,
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,
        "selected_task": selected_task,
        "total_students": total_students,
        "completed_tasks_count": completed_tasks_count,
        "average_score": average_score,
        "last_update": last_update,
        "task_map": task_map,
    }
    return render(request, 'Tier/Junior.html', context)

# This is the senior tier page of Faculty
@faculty_required
def senior_tier(request):
    # Get the logged-in faculty member using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Get active assignments for this faculty
    faculty_assignments = faculty.assignments.filter(is_active=True)
    
    if not faculty_assignments.exists():
        messages.warning(request, "No active assignments found for your account.")
        context = {
            "senior_students": [],
            "senior_leaderboard": [],
            "faculty_data": faculty,
            "faculty_assignments": [],
            "selected_task": "task1",
        }
        return render(request, 'Tier/Senior.html', context)

    # Task map for filtering Senior tier tasks
    task_map = {
        "task1": "Senior_Task_1(Collect Books)",
        "task2": "Senior_Task_2(QNA)",
        "task3": "Senior_Task_3(Collect USB)",
        "task4": "Senior_Task_4(QNA)",
        "task5": "Senior_Task_5(QNA)",
        "task6": "Senior_Task_6(Defeat Rootkit2)",
    }
    
    # Get current time in Philippine timezone
    philippine_tz = pytz.timezone('Asia/Manila')
    current_time = timezone.now().astimezone(philippine_tz)
    last_update = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # Get total students for completion rate calculation
    total_students = Student.objects.filter(
        faculty_assignment__in=faculty_assignments,
        student_status='Registered'
    ).count()

    # Initialize tracking variables
    senior_students = []
    leaderboard_students = []
    completed_tasks = 0
    total_points = 0
    total_completed_tasks = 0
    task_completion_stats = {task_id: 0 for task_id in task_map}
    students_with_tasks = set()
    students_with_points = set()
    selected_task = request.GET.get("task", "task1")
    selected_task_map = task_map.get(selected_task, task_map["task1"])

    # Process each assignment's Firebase data
    for assignment in faculty_assignments:
        students_query = db.collection("Registered_Students") \
            .where("program", "==", assignment.program) \
            .where("year_section", "==", assignment.year_section) \
            .where("semester", "==", assignment.semester) \
            .stream()

        for doc in students_query:
            student = doc.to_dict()
            student_id = student.get("student_id", doc.id)
            
            # Process individual task data
            student_total_points = 0
            student_completed_tasks = 0
            
            for task_key in task_map.values():
                task_data = student.get(task_key)
                if task_data and isinstance(task_data, dict):
                    points = int(task_data.get("points", 0))
                    if points > 0:
                        student_total_points += points
                        student_completed_tasks += 1
                        total_completed_tasks += 1

            # For progress table (filtered by selected task)
            task_data = student.get(selected_task_map)
            if task_data:
                senior_students.append({
                    "student_id": student_id,
                    "first_name": student.get("first_name", ""),
                    "last_name": student.get("last_name", ""),
                    "points": task_data.get("points", 0),
                    "total_time_completed": task_data.get("time_taken", ""),
                })

            # Add to total points if student has any
            if student_total_points > 0:
                total_points += student_total_points
                students_with_points.add(student_id)

            # Add to leaderboard if has points
            if student_total_points > 0:
                leaderboard_students.append({
                    "student_id": student_id,
                    "first_name": student.get("first_name", ""),
                    "last_name": student.get("last_name", ""),
                    "points": student_total_points,
                    "tasks_completed": student_completed_tasks,
                    "completion_percentage": (student_completed_tasks / len(task_map)) * 100
                })


    # Calculate stats for cards
    active_students = len(students_with_points)
    average_score = total_points / active_students if active_students > 0 else 0
    completed_tasks_count = total_completed_tasks

    # Sort leaderboard
    senior_leaderboard = sorted(
        leaderboard_students,
        key=lambda x: (-x["points"], -x["tasks_completed"])
    )

    context = {
        "senior_students": senior_students,
        "senior_leaderboard": senior_leaderboard,
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,
        "selected_task": selected_task,
        "total_students": total_students,
        "completed_tasks_count": completed_tasks_count,
        "average_score": average_score,
        "last_update": last_update,
        "task_map": task_map,
    }
    return render(request, 'Tier/Senior.html', context)

# This is the faculty student status page
@faculty_required
def faculty_student_status(request):
    # Get faculty using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Get active assignments for this faculty
    faculty_assignments = faculty.assignments.filter(is_active=True).annotate(
        student_count=Count('students', filter=Q(students__student_status='Registered'))
    )
    
    if not faculty_assignments.exists():
        context = {
            "students": [],
            "faculty_data": faculty,
            "faculty_assignments": [],
            "search_query": "",
            "status_filter": "all",
            "selected_program": "all",
            "selected_year_section": "all",
            "selected_semester": "all",
            "sections": [],
            "cs_students": 0,
            "it_students": 0,
            "program_total": 0,
            "section_total": 0,
            "active_students_count": 0,
            "inactive_students_count": 0,
        }
        return render(request, 'Students/student-status.html', context)

    # Get filter values from request
    selected_program = request.GET.get('program', 'all')
    selected_year_section = request.GET.get('year_section', 'all')
    selected_semester = request.GET.get('semester', 'all')
    selected_status = request.GET.get('status', 'all').lower()
    search_query = request.GET.get('search', '').strip()

    # Get unique sections from faculty assignments
    sections = faculty_assignments.values_list('year_section', flat=True).distinct()

    # Base query for students
    students_query = Student.objects.filter(faculty_assignment__in=faculty_assignments)

    # Apply filters
    if selected_program != 'all':
        students_query = students_query.filter(faculty_assignment__program=selected_program)

    if selected_year_section != 'all':
        students_query = students_query.filter(faculty_assignment__year_section=selected_year_section)

    if selected_semester != 'all':
        students_query = students_query.filter(faculty_assignment__semester=selected_semester)

    # Apply status filter
    if selected_status == 'completed':
        students_query = students_query.filter(student_status='Completed')
    elif selected_status in ['drop-out', 'dropout']:
        students_query = students_query.filter(student_status='Drop-out')
    elif selected_status == 'registered':
        students_query = students_query.filter(student_status='Registered')

    # Apply search filter
    if search_query:
        students_query = students_query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )

    # Calculate counts
    cs_students_count = Student.objects.filter(
        student_status='Registered', 
        faculty_assignment__program='Computer Science',
        faculty_assignment__is_active=True
    ).count()
    
    it_students_count = Student.objects.filter(
        student_status='Registered', 
        faculty_assignment__program='Information Technology',
        faculty_assignment__is_active=True
    ).count()

    section_total = students_query.count()
    program_total = Student.objects.filter(
        faculty_assignment__in=faculty_assignments,
        student_status='Registered'
    ).count()

    # --- Active/Inactive Students Logic (Firebase) ---
    # Define all task fields to check for activity
    task_fields = [
        # Novice Tasks
        "Novice_Task_1(Collect Books)",
        "Novice_Task_2(Collect USB)",
        "Novice_Task_3(QNA)",
        "Novice_Task_4_(Defeat Rootkit)",
        # Junior Tasks
        "Junior_Task_1(Collect Books)",
        "Junior_Task_2(Caesar's QNA)",
        "Junior_Task_3(Collect USB)", 
        "Junior_Task_4(Bellaso's QNA)",
        "Junior_Task_5(QNA)",
        "Junior_Task_6(Defeat Serpentix2)",
        # Senior Tasks
        "Senior_Task_1(Collect Books)",
        "Senior_Task_2(QNA)",
        "Senior_Task_3(Collect USB)",
        "Senior_Task_4(QNA)",
        "Senior_Task_5(QNA)",
        "Senior_Task_6(Defeat Rootkit2)"
    ]

    active_students_count = 0
    inactive_students_count = 0

    # Get only REGISTERED student IDs from the faculty's assignments for active/inactive check
    registered_student_ids = list(Student.objects.filter(
        faculty_assignment__in=faculty_assignments, 
        student_status='Registered'
    ).values_list('student_id', flat=True))

    # Check Firebase for each registered student's activity
    for student_id in registered_student_ids:
        try:
            # Get student document from Firebase
            doc_ref = db.collection('Registered_Students').document(student_id).get()
            
            if doc_ref.exists:
                student_data = doc_ref.to_dict()
                has_tasks = False
                
                # Check if any task field exists in the student's document
                for task_field in task_fields:
                    if task_field in student_data:
                        has_tasks = True
                        break
                
                if has_tasks:
                    active_students_count += 1
                else:
                    inactive_students_count += 1
            else:
                # Student not found in Firebase = inactive
                inactive_students_count += 1
                
        except Exception as e:
            # If there's an error accessing Firebase, consider student inactive
            print(f"Error checking Firebase for student {student_id}: {e}")
            inactive_students_count += 1

    # Pagination
    paginator = Paginator(students_query, 10) # 10 students per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "students": page_obj,
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,
        "search_query": search_query,
        "selected_status": selected_status,
        "selected_program": selected_program,
        "selected_year_section": selected_year_section,
        "selected_semester": selected_semester,
        "sections": sections,
        "page_obj": page_obj,
        "paginator": paginator,
        "cs_students": cs_students_count,
        "it_students": it_students_count,
        "program_total": program_total,
        "section_total": section_total,
        "active_students_count": active_students_count,
        "inactive_students_count": inactive_students_count,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/student-status-content.html', context)
    else:
        return render(request, 'Students/student-status.html', context)


# CSV Export for Students
@faculty_required
def export_student_csv(request):
    try:
        faculty_id = request.session.get('faculty_id')
        if not faculty_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('faculty-student-list')
        faculty = Faculty.objects.get(faculty_id=faculty_id)

        faculty_assignments = faculty.assignments.filter(is_active=True)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Student ID',
            'First Name', 
            'Last Name',
            'Middle Initial',
            'Program',
            'Year Section', 
            'Semester',
            'Status'
        ])
        
        # Get students from all active faculty assignments
        students = Student.objects.filter(
            faculty_assignment__in=faculty_assignments
        ).order_by('student_id')
        
        for student in students:
            writer.writerow([
                student.student_id,
                student.first_name,
                student.last_name,
                student.middle_initial or '',
                student.faculty_assignment.program,
                student.faculty_assignment.year_section,
                student.faculty_assignment.semester,
                student.student_status
            ])
        
        return response
        
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('login')

# Excel Export for Students
@faculty_required
def export_student_excel(request):
    """Export student data to Excel file"""
    try:
        faculty_id = request.session.get('faculty_id')
        if not faculty_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('faculty-student-list')
        faculty = Faculty.objects.get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('login')
    
    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Students Export"
    
    # Define headers
    headers = [
        'Student ID',
        'First Name', 
        'Last Name',
        'Middle Initial',
        'Program',
        'Year Section',
        'Semester',
        'Status'
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
    
    # Get student data and add to worksheet
    students = Student.objects.filter(faculty=faculty).order_by('student_id')
    for row, student in enumerate(students, 2):
        data = [
            student.student_id,
            student.first_name,
            student.last_name,
            student.middle_initial or '',
            student.faculty.program,
            student.faculty.year_section,
            student.faculty.semester,
            student.student_status
        ]
        
        for col, value in enumerate(data, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Add status color coding
            if col == 8:  # Status column
                if value == 'Completed':
                    cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
                elif value == 'Drop-out':
                    cell.fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
                else:  # Registered
                    cell.fill = PatternFill(start_color="E8F5E8", end_color="E8F5E8", fill_type="solid")
    
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
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="students_export.xlsx"'
    
    wb.save(response)
    return response

# CSV Import for Students
@faculty_required
def import_student(request):
    """Import student data from CSV or Excel file"""
    try:
        faculty_id = request.session.get('faculty_id')
        if not faculty_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('faculty-student-list')
            
        faculty = Faculty.objects.get(faculty_id=faculty_id)
        faculty_assignments = faculty.assignments.filter(is_active=True)
        
        if not faculty_assignments.exists():
            messages.error(request, "No active assignments found. Please set up class assignments first.")
            return redirect('faculty-student-list')

        # Enhanced debug information
        print(f"=== IMPORT DEBUG ===")
        print(f"Request method: {request.method}")
        print(f"Files in request: {list(request.FILES.keys())}")
        print(f"POST data keys: {list(request.POST.keys())}")
        print(f"Content type: {request.content_type}")
        
        if 'csv_file' in request.FILES:
            file_obj = request.FILES['csv_file']
            print(f"File name: {file_obj.name}")
            print(f"File size: {file_obj.size}")
            print(f"File content type: {file_obj.content_type}")

        if request.method == 'POST' and request.FILES.get('csv_file'):
            uploaded_file = request.FILES['csv_file']
            success_count = 0
            error_count = 0
            errors = []
            rows = []
            
            print(f"Processing file: {uploaded_file.name}")
            
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            
            # Get file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # Validate file type
            if file_extension not in ['csv', 'xlsx', 'xls']:
                messages.error(request, 'Please upload a CSV or Excel file (.csv, .xlsx, .xls).')
                return redirect('faculty-student-list')
            
            try:
                # Process based on file type
                if file_extension == 'csv':
                    # Handle CSV file
                    try:
                        uploaded_file.seek(0)  # Reset file pointer
                        file_data = uploaded_file.read().decode('utf-8-sig')
                        io_string = io.StringIO(file_data)
                        reader = csv.DictReader(io_string)
                        rows = list(reader)
                        
                        print(f"CSV rows found: {len(rows)}")
                        
                        # Validate CSV headers
                        if not rows:
                            messages.error(request, 'The file appears to be empty.')
                            return redirect('faculty-student-list')
                            
                        required_headers = ['Student ID', 'First Name', 'Last Name', 'Program', 'Year Section', 'Semester']
                        file_headers = list(rows[0].keys()) if rows else []
                        missing_headers = [h for h in required_headers if h not in file_headers]
                        
                        print(f"File headers: {file_headers}")
                        print(f"Missing headers: {missing_headers}")
                        
                        if missing_headers:
                            messages.error(request, f'Missing required columns: {", ".join(missing_headers)}')
                            return redirect('faculty-student-list')
                            
                    except UnicodeDecodeError as e:
                        print(f"Unicode decode error: {e}")
                        messages.error(request, 'Invalid CSV file encoding. Please ensure the file is UTF-8 encoded.')
                        return redirect('faculty-student-list')
                else:
                    # Handle Excel file (.xlsx or .xls)
                    try:
                        uploaded_file.seek(0)  # Reset file pointer
                        workbook = load_workbook(uploaded_file, read_only=True)
                        worksheet = workbook.active
                        
                        # Get header row
                        headers = [str(cell.value).strip() if cell.value else '' for cell in worksheet[1]]
                        
                        print(f"Excel headers: {headers}")
                        
                        # Validate headers
                        required_headers = ['Student ID', 'First Name', 'Last Name', 'Program', 'Year Section', 'Semester']
                        missing_headers = [h for h in required_headers if h not in headers]
                        
                        print(f"Missing headers: {missing_headers}")
                        
                        if missing_headers:
                            messages.error(request, f'Missing required columns: {", ".join(missing_headers)}')
                            return redirect('faculty-student-list')
                        
                        # Convert Excel data to dictionary format
                        for row in worksheet.iter_rows(min_row=2, values_only=True):
                            if any(row):  # Skip empty rows
                                row_dict = {}
                                for i, value in enumerate(row):
                                    if i < len(headers) and headers[i]:
                                        row_dict[headers[i]] = str(value).strip() if value is not None else ''
                                rows.append(row_dict)
                        
                        print(f"Excel rows found: {len(rows)}")
                                
                    except Exception as e:
                        print(f"Excel processing error: {e}")
                        messages.error(request, f'Error reading Excel file: {str(e)}')
                        return redirect('faculty-student-list')

                print(f"Processing {len(rows)} rows")

                # Process each row
                for row_num, row in enumerate(rows, start=2):
                    try:
                        student_id = row.get('Student ID', '').strip()
                        first_name = row.get('First Name', '').strip()
                        last_name = row.get('Last Name', '').strip()
                        middle_initial = row.get('Middle Initial', '').strip()
                        program = row.get('Program', '').strip()
                        year_section = row.get('Year Section', '').strip()
                        semester = row.get('Semester', '').strip()
                        
                        print(f"Processing row {row_num}: {student_id} - {first_name} {last_name}")
                        
                        # Validate required fields
                        if not all([student_id, first_name, last_name, program, year_section, semester]):
                            errors.append(f'Row {row_num}: Missing required fields')
                            error_count += 1
                            continue

                        # Find matching faculty assignment
                        matching_assignment = faculty_assignments.filter(
                            program=program,
                            year_section=year_section,
                            semester=semester
                        ).first()

                        if not matching_assignment:
                            errors.append(
                                f'Row {row_num}: Program ({program}), Year Section ({year_section}), '
                                f'or Semester ({semester}) does not match any of your active assignments'
                            )
                            error_count += 1
                            continue
                        
                        # Check if student already exists
                        if Student.objects.filter(student_id=student_id).exists():
                            errors.append(f'Row {row_num}: Student ID "{student_id}" already exists')
                            error_count += 1
                            continue
                        
                        # Create student with matched faculty assignment
                        student = Student.objects.create(
                            student_id=student_id,
                            first_name=first_name,
                            last_name=last_name,
                            middle_initial=middle_initial,
                            faculty_assignment=matching_assignment,
                            student_status='Registered'
                        )
                        
                        # Create Firestore record
                        firestore_data = {
                            'student_id': student_id,
                            'first_name': first_name,
                            'last_name': last_name,
                            'middle_initial': middle_initial,
                            'program': matching_assignment.program,
                            'year_section': matching_assignment.year_section,
                            'semester': matching_assignment.semester,
                        }
                        
                        try:
                            db.collection('Registered_Students').document(student_id).set(firestore_data)
                            success_count += 1
                            print(f"Successfully imported: {student_id}")
                        except Exception as e:
                            print(f"Failed to create Firestore record for {student_id}: {e}")
                            student.delete()
                            errors.append(f'Row {row_num}: Failed to create Firestore record')
                            error_count += 1
                            continue
                            
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}")
                        errors.append(f'Row {row_num}: {str(e)}')
                        error_count += 1
                        continue

                # Show results
                if success_count > 0:
                    messages.success(request, f'Successfully imported {success_count} students.')
                
                if error_count > 0:
                    error_message = f'{error_count} rows had errors:\n' + '\n'.join(errors[:10])
                    if len(errors) > 10:
                        error_message += f'\n... and {len(errors) - 10} more errors.'
                    messages.error(request, error_message)
                    
            except Exception as e:
                print(f"Exception during file processing: {e}")
                messages.error(request, f'Error processing file: {str(e)}')
                
        else:
            print("No file uploaded or invalid request method")
            if request.method == 'POST':
                messages.error(request, "No file was uploaded. Please select a file to import.")
            else:
                messages.info(request, "Invalid request method.")
                
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
    except Exception as e:
        print(f"Unexpected error in import_student: {e}")
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        
    return redirect('faculty-student-list')

# Download CSV Template
@faculty_required
def download_student_csv_template(request):
    """Download a CSV template for student import"""
    try:
        # Get faculty and active assignment info
        faculty_id = request.session.get('faculty_id')
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
        default_assignment = faculty.assignments.filter(is_active=True).first()
        
        if not default_assignment:
            messages.error(request, "No active assignments found. Please set up class assignments first.")
            return redirect('faculty-student-list')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_import_template.csv"'
        
        writer = csv.writer(response)
        # Write CSV header
        writer.writerow([
            'Student ID',
            'First Name', 
            'Last Name',
            'Middle Initial',
            'Program',
            'Year Section',
            'Semester'
        ])
        
        # Add sample row with faculty's assignment details
        writer.writerow([
            'S2024001',
            'Juan',
            'Dela Cruz',
            'M',
            default_assignment.program,
            default_assignment.year_section,
            default_assignment.semester
        ])
        
        return response
        
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('faculty-student-list')

# Download Excel Template
@faculty_required
def download_student_excel_template(request):
    """Download an Excel template for student import"""
    try:
        # Get faculty and assignments using session
        faculty_id = request.session.get('faculty_id')
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
        faculty_assignments = faculty.assignments.filter(is_active=True)
        
        if not faculty_assignments.exists():
            messages.error(request, "No active assignments found. Please set up class assignments first.")
            return redirect('faculty-student-list')
            
        default_assignment = faculty_assignments.first()
            
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Students Template"
        
        # Define headers
        headers = [
            'Student ID',
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
        
        # Add sample data with faculty's assignment details
        sample_data = [
            'S2024001',
            'Juan',
            'Dela Cruz',
            'M',
            default_assignment.program,
            default_assignment.year_section,
            default_assignment.semester
        ]
        
        for col, value in enumerate(sample_data, 1):
            cell = ws.cell(row=2, column=col, value=value)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center")
        
        # Add instructions in a separate sheet
        instructions_ws = wb.create_sheet("Instructions")
        
        # Basic instructions with updated column information
        instructions = [
            ["Student Import Instructions", ""],
            ["", ""],
            [f"Faculty: {faculty.first_name} {faculty.last_name}", ""],
            ["", ""],
            ["Your Active Class Assignment:", ""],
            [f"• Program: {default_assignment.program}", ""],
            [f"• Year Section: {default_assignment.year_section}", ""],
            [f"• Semester: {default_assignment.semester}", ""],
            ["", ""],
            ["Required Columns:", ""],
            ["Student ID", "Unique identifier for the student (Required)"],
            ["First Name", "Student's first name (Required)"],
            ["Last Name", "Student's last name (Required)"],
            ["Middle Initial", "Student's middle initial (Optional)"],
            ["Program", f"Must match your program: {default_assignment.program}"],
            ["Year Section", f"Must match your section: {default_assignment.year_section}"],
            ["Semester", f"Must match your semester: {default_assignment.semester}"],
            ["", ""],
            ["Important Notes:", ""],
            ["• All imported students will automatically be set as 'Registered'", ""],
            ["• Program, Year Section, and Semester must match your assignment exactly", ""],
            ["• Existing Student IDs will be skipped", ""],
            ["• Make sure to follow the exact column names as shown in the template", ""],
            ["• Remove the sample data before importing your actual data", ""],
        ]
        
        # Style the instructions sheet
        for row, (instruction, detail) in enumerate(instructions, 1):
            cell1 = instructions_ws.cell(row=row, column=1, value=instruction)
            cell2 = instructions_ws.cell(row=row, column=2, value=detail)
            
            if row == 1:  # Title
                cell1.font = Font(bold=True, size=14)
            elif instruction and instruction.endswith(":"):  # Section headers
                cell1.font = Font(bold=True)
            elif instruction.startswith("•"):  # List items
                cell1.font = Font(color="0066CC")
        
        # Adjust column widths for both sheets
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
        response['Content-Disposition'] = 'attachment; filename="student_import_template.xlsx"'
        
        wb.save(response)
        return response
        
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('faculty-student-list')
    except Exception as e:
        messages.error(request, f"Error creating template: {str(e)}")
        return redirect('faculty-student-list')


@faculty_required
def faculty_delete_archived_student(request, student_id):
    if request.method == 'POST':
        try:
            # Get the archived student
            archived_student = ArchivedStudent.objects.get(student_id=student_id)
            
            # Get faculty from session to verify ownership
            faculty_id = request.session.get('faculty_id')
            faculty = Faculty.objects.get(faculty_id=faculty_id)
            
            # Check if this archived student belongs to the current faculty
            if archived_student.faculty != faculty:
                messages.error(request, "You don't have permission to delete this student.")
                return redirect('faculty-student-list')
            
            # Delete the archived student permanently
            archived_student.delete()
            
            messages.success(request, f"Student {student_id} has been permanently deleted from the archive.")
            
        except ArchivedStudent.DoesNotExist:
            messages.error(request, "Archived student not found.")
        except Faculty.DoesNotExist:
            messages.error(request, "Faculty profile not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('archived_students_list')

@faculty_required
def studentData(request):
    # Get faculty using session
    faculty_id = request.session.get('faculty_id')
    if not faculty_id:
        messages.error(request, "Session expired. Please login again.")
        return redirect('sentinels_login')  
    
    try:
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')

    # Get active assignments for this faculty
    faculty_assignments = faculty.assignments.filter(is_active=True)
    
    if not faculty_assignments.exists():
        context = {
            "faculty_data": faculty,
            "total_students": 0,
            "average_completion": 0,
            "active_students": 0,
            "inactive_students": 0,
            "students": []
        }
        return render(request, 'Students/studentData.html', context)

    # Get total students count
    total_students = Student.objects.filter(
        faculty_assignment__in=faculty_assignments,
        student_status='Registered'
    ).count()

    search_query = request.GET.get('search', '').strip()

    # Get students for table display
    students = Student.objects.filter(
        faculty_assignment__in=faculty_assignments,
        student_status='Registered'
    ).order_by('last_name')

    # Apply search filter
    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )


    # Firebase task completion check
    task_fields = [
        # Novice Tasks
        "Novice_Task_1(Collect Books)", "Novice_Task_2(Collect USB)",
        "Novice_Task_3(QNA)", "Novice_Task_4_(Defeat Rootkit)",
        # Junior Tasks
        "Junior_Task_1(Collect Books)", "Junior_Task_2(Caesar's QNA)",
        "Junior_Task_3(Collect USB)", "Junior_Task_4(Bellaso's QNA)",
        "Junior_Task_5(QNA)", "Junior_Task_6(Defeat Serpentix2)",
        # Senior Tasks
        "Senior_Task_1(Collect Books)", "Senior_Task_2(QNA)",
        "Senior_Task_3(Collect USB)", "Senior_Task_4(QNA)",
        "Senior_Task_5(QNA)", "Senior_Task_6(Defeat Rootkit2)"
    ]

    total_tasks = len(task_fields)
    total_completed_tasks = 0
    active_students = 0
    inactive_students = 0
    # Enhanced student data with task information
    enhanced_students = []

    # Check Firebase for each student's activity
    for student in students:
        try:
            doc_ref = db.collection('Registered_Students').document(student.student_id).get()
            if doc_ref.exists:
                student_data = doc_ref.to_dict()
                completed_tasks = 0
                task_details = {
                    'novice': {},
                    'junior': {},
                    'senior': {}
                }
                
                # Count completed tasks and organize task data by tier
                for task_field in task_fields:
                    if task_field in student_data and isinstance(student_data[task_field], dict):
                        task_info = student_data[task_field]
                        points = task_info.get("points", 0)
                        
                        if points > 0:
                            completed_tasks += 1
                            total_completed_tasks += 1
                            
                        # Categorize task by tier
                        if task_field.startswith("Novice"):
                            task_details['novice'][task_field] = {
                                'points': points,
                                'completedAt': task_info.get('completed_at'),
                                'time_taken': task_info.get('time_taken', '')
                            }
                        elif task_field.startswith("Junior"):
                            task_details['junior'][task_field] = {
                                'points': points,
                                'completedAt': task_info.get('completed_at'),
                                'time_taken': task_info.get('time_taken', '')
                            }
                        elif task_field.startswith("Senior"):
                            task_details['senior'][task_field] = {
                                'points': points,
                                'completedAt': task_info.get('completed_at'),
                                'time_taken': task_info.get('time_taken', '')
                            }

                # Update student status
                if completed_tasks > 0:
                    active_students += 1
                else:
                    inactive_students += 1

                # Add enhanced student data
                enhanced_students.append({
                    'student': student,
                    'task_details': task_details,
                    'completed_tasks': completed_tasks,
                    'total_points': sum(task['points'] for tier in task_details.values() 
                                     for task in tier.values())
                })
            else:
                inactive_students += 1
                enhanced_students.append({
                    'student': student,
                    'task_details': {'novice': {}, 'junior': {}, 'senior': {}},
                    'completed_tasks': 0,
                    'total_points': 0
                })
                
        except Exception as e:
            print(f"Error checking Firebase for student {student.student_id}: {e}")
            inactive_students += 1
            enhanced_students.append({
                'student': student,
                'task_details': {'novice': {}, 'junior': {}, 'senior': {}},
                'completed_tasks': 0,
                'total_points': 0
            })

    # Calculate average completion
    average_completion = (total_completed_tasks / (total_students * total_tasks) * 100) if total_students > 0 else 0

    context = {
        "search_query": search_query,
        "faculty_data": faculty,
        "total_students": total_students,
        "average_completion": f"{average_completion:.1f}",
        "active_students": active_students,
        "inactive_students": inactive_students,
        "students": enhanced_students,
        "task_fields": task_fields,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'Students/contents/studentData-content.html', context)
    else:
        return render(request, 'Students/studentData.html', context)
    

@faculty_required
def studentDataModal(request, student_id):
    try:
        # Get student data from Firebase
        doc_ref = db.collection('Registered_Students').document(student_id).get()
        faculty_id = request.session.get('faculty_id')
        
        if not doc_ref.exists:
            return JsonResponse({'error': 'Student data not found'}, status=404)
        
        student_data = doc_ref.to_dict()
        
        # Organize task data by tier
        task_details = {
            'novice': {},
            'junior': {},
            'senior': {}
        }

        # Define task fields
        task_fields = [
            # Novice Tasks
            "Novice_Task_1(Collect Books)",
            "Novice_Task_2(Collect USB)",
            "Novice_Task_3(QNA)",
            "Novice_Task_4_(Defeat Rootkit)",
            # Junior Tasks
            "Junior_Task_1(Collect Books)",
            "Junior_Task_2(Caesar's QNA)",
            "Junior_Task_3(Collect USB)",
            "Junior_Task_4(Bellaso's QNA)",
            "Junior_Task_5(QNA)",
            "Junior_Task_6(Defeat Serpentix2)",
            # Senior Tasks
            "Senior_Task_1(Collect Books)",
            "Senior_Task_2(QNA)",
            "Senior_Task_3(Collect USB)",
            "Senior_Task_4(QNA)",
            "Senior_Task_5(QNA)",
            "Senior_Task_6(Defeat Rootkit2)"
        ]

        # Process task data
        for task_field in task_fields:
            if task_field in student_data and isinstance(student_data[task_field], dict):
                task_info = student_data[task_field]
                tier = 'novice' if 'Novice' in task_field else 'junior' if 'Junior' in task_field else 'senior'
                task_details[tier][task_field] = {
                    'points': task_info.get('points', 0),
                    'completedAt': task_info.get('completed_at'),
                    'time_taken': task_info.get('time_taken', '')
                }

        # Get deadlines for this faculty
        deadlines_doc = db.collection('Activity Deadlines').document(faculty_id).get()
        deadlines_data = deadlines_doc.to_dict() if deadlines_doc.exists else {}
        
        # Task completion and deadline status
        late_completions = []
        
        # Process each task with deadline
        for task_key, deadline_info in deadlines_data.items():
            task_data = student_data.get(task_key)
            if task_data and isinstance(task_data, dict):
                deadline_date = deadline_info.get('deadline_date')
                deadline_time = deadline_info.get('deadline_time')
                
                if check_late_completions(task_data, deadline_date, deadline_time):
                    late_completions.append({
                        'task_name': task_key,
                        'deadline': f"{deadline_date} {deadline_time}",
                        'completed_at': task_data['completed_at'].strftime('%Y-%m-%d %H:%M'),
                        'points': task_data.get('points', 0)
                    })

        context = {
            'student_id': student_id,
            'task_details': task_details,
            'student_name': f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}",
            'late_completions': sorted(late_completions, key=lambda x: x['completed_at']),
        }

        return JsonResponse(context)
        
    except Exception as e:
        print(f"Error fetching modal data for student {student_id}: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    


@csrf_exempt
@faculty_required
def saveActivityDeadline(request):
    if request.method == "POST":
        try:
            print("=== SAVE DEADLINE DEBUG ===")
            print(f"Raw request body: {request.body}")
            
            data = json.loads(request.body)
            print(f"Parsed data: {data}")
            
            faculty_id = request.session.get('faculty_id')
            print(f"Faculty ID from session: {faculty_id}")
            
            if not faculty_id:
                print("ERROR: No faculty_id in session")
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Session expired. Please login again.'
                })
            
            title = data.get('title')
            tier = data.get('tier')
            date = data.get('date')
            time = data.get('time')
            
            print(f"Extracted - Title: {title}, Tier: {tier}, Date: {date}, Time: {time}")
            
            # Add faculty validation
            try:
                faculty = Faculty.objects.get(faculty_id=faculty_id)
                print(f"Faculty found: {faculty.faculty_id}")
            except Faculty.DoesNotExist:
                print(f"ERROR: Faculty not found for ID: {faculty_id}")
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Faculty profile not found.'
                })

            # Map combined tasks to their individual Firebase task keys
            task_mapping = {
                # Novice tasks
                'Novice Task 1': [
                    "Novice_Task_1(Collect Books)",
                ],
                'Novice Task 2': [
                    "Novice_Task_2(Collect USB)",
                ],
                'Novice Task 3': [
                    "Novice_Task_3(QNA)"
                ],
                'Novice Boss Battle': [
                    "Novice_Task_4(Defeat Rootkit)"
                ],
                # Junior tasks
                'Junior Task 1': [
                    "Junior_Task_1(Collect Books)",
                    "Junior_Task_2(Caesar's QNA)"
                ],
                'Junior Task 2': [
                    "Junior_Task_3(Collect USB)",
                    "Junior_Task_4(Bellaso's QNA)"
                ],
                'Junior Task 3': [
                    "Junior_Task_5(QNA)"
                ],
                'Junior Boss Battle': [
                    "Junior_Task_6(Defeat Serpentix2)"
                ],
                # Senior tasks
                'Senior Task 1': [
                    "Senior_Task_1(Collect Books)",
                    "Senior_Task_2(QNA)"
                ],
                'Senior Task 2': [
                    "Senior_Task_3(Collect USB)",
                    "Senior_Task_4(QNA)"
                ],
                'Senior Task 3': [
                    "Senior_Task_5(QNA)"
                ],
                'Senior Boss Battle': [
                    "Senior_Task_6(Defeat Rootkit2)"
                ]
            }

            # Get the Firebase task keys for the selected activity
            firebase_tasks = task_mapping.get(title, [])
            print(f"Firebase tasks to create: {firebase_tasks}")
            
            if not firebase_tasks:
                print(f"ERROR: No mapping found for title: {title}")
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Invalid task title: {title}'
                })

            # Create deadline data for each Firebase task
            deadline_data = {}
            for task_key in firebase_tasks:
                deadline_data[task_key] = {
                    'tier': tier,
                    'title': task_key,
                    'deadline_date': date,
                    'deadline_time': time,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'display_title': title
                }
            
            print(f"Deadline data to save: {deadline_data}")

            # Save all deadlines in a single operation
            print(f"Saving to Firestore collection 'Activity Deadlines' document '{faculty_id}'")
            db.collection('Activity Deadlines').document(faculty_id).set(
                deadline_data, 
                merge=True
            )
            
            print("SUCCESS: Deadline saved to Firestore")
            print("=== END DEBUG ===")
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Deadline set successfully for {title}!'
            })

        except json.JSONDecodeError as e:
            print(f"JSON DECODE ERROR: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': f'Invalid JSON data: {str(e)}'
            })
        except Exception as e:
            print(f"GENERAL ERROR in saveActivityDeadline: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error', 
                'message': f'Failed to save deadline: {str(e)}'
            })
            
    print("ERROR: Not a POST request")
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


# This is the remove deadline of Activity process
@csrf_exempt
@faculty_required
def remove_deadline(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get('title')
            
            faculty_id = request.session.get('faculty_id')
            
            if not faculty_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Session expired. Please login again.'
                })
            
            # Add faculty validation
            try:
                faculty = Faculty.objects.get(faculty_id=faculty_id)
            except Faculty.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Faculty profile not found.'
                })
            
            if title and faculty_id:
                # Map display title to Firebase task keys
                task_mapping = {
                    # Novice tasks
                    'Novice Task 1': [
                        "Novice_Task_1(Collect Books)",
                    ],
                    'Novice Task 2': [
                        "Novice_Task_2(Collect USB)",
                    ],
                    'Novice Task 3': [
                        "Novice_Task_3(QNA)"
                    ],
                    'Novice Boss Battle': [
                        "Novice_Task_4(Defeat Rootkit)"
                    ],
                    # Junior tasks
                    'Junior Task 1': [
                        "Junior_Task_1(Collect Books)",
                        "Junior_Task_2(Caesar's QNA)"
                    ],
                    'Junior Task 2': [
                        "Junior_Task_3(Collect USB)",
                        "Junior_Task_4(Bellaso's QNA)"
                    ],
                    'Junior Task 3': [
                        "Junior_Task_5(QNA)"
                    ],
                    'Junior Boss Battle': [
                        "Junior_Task_6(Defeat Serpentix2)"
                    ],
                    # Senior tasks
                    'Senior Task 1': [
                        "Senior_Task_1(Collect Books)",
                        "Senior_Task_2(QNA)"
                    ],
                    'Senior Task 2': [
                        "Senior_Task_3(Collect USB)",
                        "Senior_Task_4(QNA)"
                    ],
                    'Senior Task 3': [
                        "Senior_Task_5(QNA)"
                    ],
                    'Senior Boss Battle': [
                        "Senior_Task_6(Defeat Rootkit2)"
                    ]
                }

                firebase_tasks = task_mapping.get(title, [])
                
                if firebase_tasks:
                    # Remove each Firebase task key
                    update_data = {}
                    for task_key in firebase_tasks:
                        update_data[task_key] = firestore.DELETE_FIELD
                    
                    db.collection('Activity Deadlines').document(faculty_id).update(update_data)
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': f'Deadline for "{title}" removed successfully.'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid task title.'
                    })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing title or faculty information.'
                })
                
        except Exception as e:
            print(f"Error in remove_deadline: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to remove deadline: {str(e)}'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@faculty_required
def check_late_completions(task_data, deadline_date, deadline_time):
    """Check if task was completed after deadline"""
    if not task_data or not deadline_date or not deadline_time:
        return False
        
    try:
        # Combine deadline date and time
        deadline_str = f"{deadline_date} {deadline_time}"
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
        
        # Get completion timestamp
        completed_at = task_data.get('completed_at')
        if not completed_at:
            return False
            
        # Convert completion timestamp to datetime
        completion_time = datetime.fromtimestamp(completed_at.timestamp())
        
        # Task is late if completed after deadline
        return completion_time > deadline
    except:
        return False


@faculty_required
def get_late_completions(request, task_title):
    try:
        faculty_id = request.session.get('faculty_id')
        
        # Get deadline info for this task
        deadline_doc = db.collection('Activity Deadlines').document(faculty_id).get()
        if not deadline_doc.exists:
            return JsonResponse({'late_completions': []})
            
        deadline_data = deadline_doc.to_dict()
        
        # Get all students' data
        students_ref = db.collection('Registered_Students').where('faculty_id', '==', faculty_id).stream()
        
        late_completions = []
        for student in students_ref:
            student_data = student.to_dict()
            
            # Check each task that matches the display title
            for task_key, deadline_info in deadline_data.items():
                if deadline_info.get('display_title') == task_title:
                    task_data = student_data.get(task_key)
                    if task_data and isinstance(task_data, dict):
                        # Check if completion was late
                        if check_late_completions(task_data, 
                                                deadline_info.get('deadline_date'),
                                                deadline_info.get('deadline_time')):
                            late_completions.append({
                                'student_name': f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}",
                                'student_id': student_data.get('student_id', ''),
                                'completed_at': task_data['completed_at'].strftime('%Y-%m-%d %H:%M'),
                                'points': task_data.get('points', 0)
                            })
        
        return JsonResponse({'late_completions': late_completions})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@faculty_required
def facultyDevinnovateSection(request):
    # --- PostgreSQL Data Fetching ---
    try:
        # Get faculty_id from session instead of request.user.username
        faculty_id = request.session.get('faculty_id')
        if not faculty_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect('sentinels_login')
            
        faculty = Faculty.objects.prefetch_related('assignments').get(faculty_id=faculty_id)
        
        # Get active assignments for this faculty
        faculty_assignments = faculty.assignments.filter(is_active=True)
        
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('sentinels_login')
    

    context = {
        "faculty_data": faculty,
        "faculty_assignments": faculty_assignments,
    }

    if request.headers.get('HX-Request'):
        # HTMX request: return only the main content
        return render(request, 'Devinnovate/contents/faculty-devinnovate-content.html', context)
    else:
        # Normal request: return the full page
        return render(request, 'Devinnovate/faculty-devinnovate.html', context)





