from django import forms
from django.contrib.auth.hashers import make_password
from Faculty.models import Faculty, FacultyAssignment
from django.db import transaction
import json

class AddFacultyForm(forms.ModelForm):
    assignments = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Faculty
        fields = ['faculty_id', 'first_name', 'last_name', 'middle_initial']
    
    def clean_faculty_id(self):
        faculty_id = self.cleaned_data['faculty_id']
        if Faculty.objects.filter(faculty_id=faculty_id).exists():
            raise forms.ValidationError("Faculty ID already exists.")
        return faculty_id
    
    def clean_assignments(self):
        assignments_json = self.cleaned_data.get('assignments', '[]')
        print(f"=== FORM CLEAN ASSIGNMENTS ===")
        print(f"Raw assignments JSON: '{assignments_json}'")
        print(f"Type: {type(assignments_json)}")
        print(f"Length: {len(assignments_json) if assignments_json else 'None'}")
        
        if not assignments_json or assignments_json == '[]':
            print("No assignments provided or empty array")
            raise forms.ValidationError("At least one assignment is required.")
        
        try:
            assignments = json.loads(assignments_json)
            print(f"Parsed assignments: {assignments}")
            print(f"Number of assignments: {len(assignments)}")
            
            if not assignments:
                raise forms.ValidationError("At least one assignment is required.")
            
            # Validate each assignment
            validated_assignments = []
            for i, assignment in enumerate(assignments):
                print(f"Processing assignment {i}: {assignment}")
                
                if not isinstance(assignment, dict):
                    raise forms.ValidationError(f"Assignment {i+1} is not a valid object.")
                
                required_fields = ['program', 'year_section', 'semester']
                missing_fields = [field for field in required_fields if field not in assignment or not assignment[field]]
                
                if missing_fields:
                    raise forms.ValidationError(f"Assignment {i+1} is missing required fields: {', '.join(missing_fields)}")
                
                # Clean and validate the assignment data
                clean_assignment = {
                    'program': str(assignment['program']).strip(),
                    'year_section': str(assignment['year_section']).strip(),
                    'semester': str(assignment['semester']).strip()
                }
                
                if clean_assignment['program'] not in ['Computer Science', 'Information Technology']:
                    raise forms.ValidationError(f"Invalid program '{clean_assignment['program']}' in assignment {i+1}.")
                
                if clean_assignment['semester'] not in ['1st Semester', '2nd Semester', 'Summer']:
                    raise forms.ValidationError(f"Invalid semester '{clean_assignment['semester']}' in assignment {i+1}.")
                
                validated_assignments.append(clean_assignment)
                print(f"Validated assignment {i}: {clean_assignment}")
            
            print(f"=== FINAL VALIDATED ASSIGNMENTS ===")
            print(f"Total: {len(validated_assignments)}")
            for i, assignment in enumerate(validated_assignments):
                print(f"  {i+1}: {assignment}")
            
            return validated_assignments
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            raise forms.ValidationError(f"Invalid assignments data format: {str(e)}")
        except Exception as e:
            print(f"Unexpected error in clean_assignments: {e}")
            raise forms.ValidationError(f"Error processing assignments: {str(e)}")
    
    def save(self, commit=True):
        if commit:
            with transaction.atomic():
                print("=== SAVING FACULTY ===")
                
                # Get assignments before creating faculty
                assignments = self.cleaned_data.get('assignments', [])
                print(f"Assignments to create: {len(assignments)}")
                
                # Create faculty instance
                faculty = Faculty.objects.create(
                    faculty_id=self.cleaned_data['faculty_id'],
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    middle_initial=self.cleaned_data.get('middle_initial', ''),
                    password=make_password("welcomeadmin"),
                    faculty_status='Continuing'
                )
                print(f"Created faculty: {faculty.faculty_id} - {faculty.first_name} {faculty.last_name}")
                
                # Verify no existing assignments (should be none for new faculty)
                existing_count = FacultyAssignment.objects.filter(faculty=faculty).count()
                print(f"Existing assignments for new faculty: {existing_count}")
                
                if existing_count > 0:
                    print(f"WARNING: New faculty already has {existing_count} assignments!")
                    # Clear them just to be safe
                    FacultyAssignment.objects.filter(faculty=faculty).delete()
                    print("Cleared existing assignments")
                
                # Create ONLY the specified assignments
                created_assignments = []
                for i, assignment_data in enumerate(assignments):
                    assignment = FacultyAssignment.objects.create(
                        faculty=faculty,
                        program=assignment_data['program'],
                        year_section=assignment_data['year_section'],
                        semester=assignment_data['semester'],
                        is_active=True
                    )
                    created_assignments.append(assignment)
                    print(f"Created assignment {i+1}: {assignment.program} - {assignment.year_section} - {assignment.semester}")
                
                print(f"=== SAVE COMPLETE ===")
                print(f"Faculty: {faculty.faculty_id}")
                print(f"Assignments created: {len(created_assignments)}")
                
                return faculty
        else:
            return super().save(commit=False)