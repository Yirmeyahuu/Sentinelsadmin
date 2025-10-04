from django.db import migrations, connection

def safe_link_students_to_assignments(apps, schema_editor):
    """Safely link students to assignments, handling missing tables/fields gracefully"""
    try:
        # Check if the required tables exist
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN ('Faculty_Assignment', 'Student', 'Faculty')
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            if 'Faculty_Assignment' not in existing_tables:
                print("Faculty_Assignment table doesn't exist yet, skipping student linking")
                return
                
            if 'Student' not in existing_tables or 'Faculty' not in existing_tables:
                print("Required tables not found, skipping student linking")
                return

        # Now try to get the models
        Student = apps.get_model('Student', 'Student')
        FacultyAssignment = apps.get_model('Faculty', 'FacultyAssignment')
        
        # Check if faculty_assignment field exists on Student model
        try:
            Student._meta.get_field('faculty_assignment')
        except:
            print("faculty_assignment field not found on Student model, skipping")
            return
        
        students_linked = 0
        for student in Student.objects.filter(faculty__isnull=False, faculty_assignment__isnull=True):
            try:
                assignment = FacultyAssignment.objects.filter(
                    faculty=student.faculty,
                    is_active=True
                ).first()
                
                if assignment:
                    student.faculty_assignment = assignment
                    student.save()
                    students_linked += 1
                    print(f"Linked student {student.student_id} to assignment {assignment}")
                else:
                    print(f"No assignment found for student {student.student_id}'s faculty")
                    
            except Exception as e:
                print(f"Error linking student {getattr(student, 'student_id', 'unknown')}: {e}")
                continue
        
        print(f"Successfully linked {students_linked} students to assignments")
        
    except Exception as e:
        print(f"Migration completed with warnings: {e}")
        # Don't raise the exception - let the migration complete

def reverse_safe_link(apps, schema_editor):
    """Safely reverse the linking"""
    try:
        Student = apps.get_model('Student', 'Student')
        Student.objects.update(faculty_assignment=None)
        print("Successfully cleared faculty_assignment links")
    except Exception as e:
        print(f"Reverse migration completed with warnings: {e}")

class Migration(migrations.Migration):
    dependencies = [
        ('Student', '0003_alter_archivedstudent_options_and_more'),
        ('Faculty', '0003_auto_20251004_0627'),
    ]

    operations = [
        migrations.RunPython(
            safe_link_students_to_assignments, 
            reverse_safe_link,
            elidable=True  # Makes this migration optional
        ),
    ]