from django import forms

class AddFacultyForm(forms.Form):
    faculty_id = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    middle_initial = forms.CharField(required=True)
    program = forms.CharField(required=True)
    year_section = forms.CharField(required=True)
    semester = forms.CharField(required=True)