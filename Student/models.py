from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=50, primary_key=True)
    student_firstName = models.CharField(max_length=100)
    student_lastName = models.CharField(max_length=100)
    student_middleInitial = models.CharField(max_length=10, blank=True)
    program = models.CharField(max_length=100)
    year_section = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.student_id} - {self.student_firstName} {self.student_lastName}"
    
    class Meta:
        db_table = 'Students'