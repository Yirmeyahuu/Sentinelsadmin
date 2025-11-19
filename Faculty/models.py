from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Faculty(models.Model):
    faculty_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    password = models.CharField(max_length=128)
    profile_image = models.ImageField(upload_to='faculty_profiles/', null=True, blank=True)
    faculty_status = models.CharField(
        max_length=20,
        choices=[('Continuing', 'Continuing'), ('Completed', 'Completed')],
        default='Continuing'
    )
    password_changed = models.BooleanField(default=False)
    password_changed_at = models.DateTimeField(null=True, blank=True)

    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the given password matches the hashed password"""
        return check_password(raw_password, self.password)
    
    def is_default_password(self):
        """Check if the user is still using the default password"""
        return not self.password_changed or check_password('welcomeadmin', self.password)

    def __str__(self):
        return f"{self.faculty_id} - {self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'Faculty'

# Add this new model
class FacultyAssignment(models.Model):
    PROGRAM_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
    ]
    
    SEMESTER_CHOICES = [
        ('1st Semester', '1st Semester'),
        ('2nd Semester', '2nd Semester'),
        ('Summer', 'Summer'),
    ]
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='assignments')
    program = models.CharField(max_length=50, choices=PROGRAM_CHOICES)
    year_section = models.CharField(max_length=20)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Faculty_Assignment'
        unique_together = ['faculty', 'program', 'year_section', 'semester']
    
    def __str__(self):
        return f"{self.faculty.faculty_id} - {self.program} {self.year_section} ({self.semester})"

class ArchivedFaculty(models.Model):
    faculty_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    faculty_status = models.CharField(max_length=20, default='Archived')
    archived_at = models.DateTimeField(auto_now_add=True)
    assignments_data = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'Archived_Faculty'

    def __str__(self):
        return f"Archived: {self.faculty_id} - {self.first_name} {self.last_name}"