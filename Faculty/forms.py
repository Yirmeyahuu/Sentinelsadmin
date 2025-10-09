from django import forms
from django.contrib.auth.hashers import make_password
from Student.models import Student
from Faculty.models import Faculty, FacultyAssignment

class AddStudentForm(forms.Form):
    student_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., 2021-00000-WN-0',
            'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
        })
    )
    middle_initial = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'M.',
            'maxlength': '2',
            'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
        })
    )
    faculty_assignment_id = forms.IntegerField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-200 rounded-lg focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
        })
    )

    def __init__(self, *args, faculty=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.faculty = faculty
        
        # Populate faculty assignment choices
        if faculty:
            assignments = FacultyAssignment.objects.filter(
                faculty=faculty,
                is_active=True
            )
            choices = [('', 'Select Class Assignment')]
            for assignment in assignments:
                label = f"{assignment.program} - {assignment.year_section} ({assignment.semester})"
                choices.append((assignment.id, label))
            
            self.fields['faculty_assignment_id'].widget.choices = choices

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError(f"Student ID {student_id} already exists.")
        return student_id

    def clean_middle_initial(self):
        middle_initial = self.cleaned_data.get('middle_initial', '').upper()
        if middle_initial and not middle_initial.endswith('.'):
            middle_initial += '.'
        return middle_initial
    
    def clean_faculty_assignment_id(self):
        faculty_assignment_id = self.cleaned_data.get('faculty_assignment_id')
        try:
            faculty_assignment = FacultyAssignment.objects.get(
                id=faculty_assignment_id,
                is_active=True
            )
            # Verify it belongs to the current faculty
            if self.faculty and faculty_assignment.faculty != self.faculty:
                raise forms.ValidationError("Invalid faculty assignment selected.")
            return faculty_assignment_id
        except FacultyAssignment.DoesNotExist:
            raise forms.ValidationError("Selected class assignment does not exist.")

    def save(self):
        """Create and save the student with faculty assignment"""
        if not self.faculty:
            raise ValueError("Faculty must be provided to save student")

        # Get form data
        student_id = self.cleaned_data['student_id']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        middle_initial = self.cleaned_data['middle_initial']
        faculty_assignment_id = self.cleaned_data['faculty_assignment_id']

        # Get the selected faculty assignment
        faculty_assignment = FacultyAssignment.objects.get(id=faculty_assignment_id)

        # Create student with default password
        student = Student.objects.create(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            middle_initial=middle_initial,
            faculty_assignment=faculty_assignment,
            student_status='Registered',
            password=make_password('welcomestudent')  # Default password
        )

        return student

class ActivityDeadlineForm(forms.Form):
    activity_id = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'w-full bg-blue-500/50 text-white p-4 rounded-2xl border border-blue-400 cursor-not-allowed'}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={'readonly': 'readonly', 'class': 'w-full bg-blue-500/50 text-white p-4 rounded-2xl border border-blue-400 cursor-not-allowed'}))
    date = forms.DateField(label="Set Date", widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full bg-blue-700 text-white p-4 rounded-2xl border border-blue-800'}))
    time = forms.TimeField(label="Set Time", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'w-full bg-blue-700 text-white p-4 rounded-2xl border border-blue-800'}))


