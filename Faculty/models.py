from django.db import models

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
        choices=[('Continuing', 'Continuing'), ('Deactivated', 'Deactivated'), ('Completed', 'Completed')],
        default='Continuing'
    )

    def __str__(self):
        return f"{self.faculty_id} - {self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'Faculty'

class ArchivedFaculty(models.Model):
    faculty_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=10, blank=True)
    program = models.CharField(max_length=100)
    year_section = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    faculty_status = models.CharField(max_length=20, default='Archived')

    def __str__(self):
        return f"{self.faculty_id} - {self.first_name} {self.last_name}"

    class Meta:
        db_table = 'ArchivedFaculty'
