from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['student_id', 'first_name', 'last_name', 'middle_initial', 'program', 'year_section', 'semester']
        widgets = {
            'semester': forms.Select(choices=[('1st Semester', '1st Semester'), ('2nd Semester', '2nd Semester')]),
            'program': forms.Select(choices=[('Computer Science', 'Computer Science'), ('Information Technology', 'Information Technology')]),
        }