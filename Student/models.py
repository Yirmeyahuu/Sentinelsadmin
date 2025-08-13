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
