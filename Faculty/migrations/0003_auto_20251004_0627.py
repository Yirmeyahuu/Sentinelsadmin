from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('Faculty', '0002_alter_archivedfaculty_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacultyAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program', models.CharField(choices=[('Computer Science', 'Computer Science'), ('Information Technology', 'Information Technology')], max_length=50)),
                ('year_section', models.CharField(max_length=20)),
                ('semester', models.CharField(choices=[('1st Semester', '1st Semester'), ('2nd Semester', '2nd Semester'), ('Summer', 'Summer')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='Faculty.faculty')),
            ],
            options={
                'db_table': 'Faculty_Assignment',
            },
        ),
        migrations.AlterUniqueTogether(
            name='facultyassignment',
            unique_together={('faculty', 'program', 'year_section', 'semester')},
        ),
    ]