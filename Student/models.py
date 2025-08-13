from django.db import models
from Faculty.models import Faculty

class Student(models.Model):
    student_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    password = models.CharField(max_length=128)
    
    student_status = models.CharField(
        max_length=20,
        choices=[('Registered', 'Registered'), ('Completed', 'Completed'), ('Dropout', 'Drop-out')],
        default='Registered'
    )

    # This ForeignKey connects each student to a specific faculty member.
    # The student's program, year, and semester are determined by their assigned faculty.
    faculty = models.ForeignKey(
        Faculty, 
        on_delete=models.CASCADE, 
        related_name='students',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'Students'

class ArchivedStudent(models.Model):
    # We use a separate AutoField for the primary key, but keep student_id for identification.
    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)

    # Store a reference to the faculty, but allow it to be null
    # in case the original faculty record is ever deleted.
    faculty = models.ForeignKey(
        Faculty, 
        on_delete=models.SET_NULL, 
        related_name='archived_students',
        null=True,
        blank=True
    )
    
    archived_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'ArchivedStudents'
        verbose_name_plural = "Archived Students"



class PendingStudent(models.Model):
    # This model holds student data before it's verified by a faculty member.
    student_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    
    # Store the intended program, year, and semester to find the right faculty
    program = models.CharField(max_length=100)
    year_section = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    
    # The password will be created and stored here, then moved on approval.
    password = models.CharField(max_length=128)
    
    # Timestamp for when the registration was submitted
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending: {self.student_id} - {self.first_name} {self.last_name}"

    class Meta:
        db_table = 'PendingStudents'
        verbose_name_plural = "Pending Students"



# --- Progress Tracking Models (Correct Location) ---

class Task(models.Model):
    """Represents a single, definable task in the game."""
    TIER_CHOICES = [
        ('Novice', 'Novice'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior'),
    ]
    task_id = models.CharField(max_length=100, primary_key=True, help_text="Unique identifier for the task, e.g., 'novice_task_1'")
    firestore_key = models.CharField(max_length=255, unique=True, help_text="The exact field name used in Firestore")
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return self.description

    class Meta:
        db_table = 'Tasks'
        ordering = ['tier', 'task_id']


class StudentTaskProgress(models.Model):
    """Links a Student to a Task they have completed."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_records')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True, help_text="Stores extra data from Firestore like score or timestamp.")

    def __str__(self):
        return f"{self.student} completed {self.task}"

    class Meta:
        db_table = 'StudentTaskProgress'
        unique_together = ('student', 'task')