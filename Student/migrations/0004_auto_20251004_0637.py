from django.db import migrations

def link_students_to_assignments(apps, schema_editor):
    Student = apps.get_model('Student', 'Student')
    FacultyAssignment = apps.get_model('Faculty', 'FacultyAssignment')
    
    for student in Student.objects.filter(faculty__isnull=False, faculty_assignment__isnull=True):
        try:
            # Get the first assignment for the student's faculty
            assignment = FacultyAssignment.objects.filter(
                faculty=student.faculty,
                is_active=True
            ).first()
            
            if assignment:
                student.faculty_assignment = assignment
                student.save()
                print(f"Linked student {student.student_id} to assignment {assignment}")
            else:
                print(f"No assignment found for student {student.student_id}'s faculty")
                
        except Exception as e:
            print(f"Error linking student {student.student_id}: {e}")

def reverse_link_students_to_assignments(apps, schema_editor):
    Student = apps.get_model('Student', 'Student')
    Student.objects.update(faculty_assignment=None)

class Migration(migrations.Migration):
    dependencies = [
        ('Student', '0003_alter_archivedstudent_options_and_more'),  # Changed to actual migration
        ('Faculty', '0003_auto_20251004_0627'),
    ]

    operations = [
        migrations.RunPython(link_students_to_assignments, reverse_link_students_to_assignments),
    ]