from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Faculty(models.Model):
    faculty_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    program = models.CharField(max_length=100)
    year_section = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    faculty_status = models.CharField(
        max_length=20,
        choices=[('Continuing', 'Continuing'), ('Completed', 'Completed')],
        default='Continuing'
    )
    # Add this field to track if password has been changed from default
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

# ArchivedFaculty remains the same
class ArchivedFaculty(models.Model):
    faculty_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    program = models.CharField(max_length=100)
    year_section = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    archived_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.faculty_id} - {self.first_name} {self.last_name}"

    class Meta:
        db_table = 'ArchivedFaculty'
        verbose_name_plural = "Archived Faculty"

class ArchivedFaculty(models.Model):
    faculty_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    program = models.CharField(max_length=100)
    year_section = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    archived_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.faculty_id} - {self.first_name} {self.last_name}"

    class Meta:
        db_table = 'ArchivedFaculty'
        verbose_name_plural = "Archived Faculty"

