import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivedFaculty',
            fields=[
                ('faculty_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_initial', models.CharField(blank=True, max_length=10)),
                ('faculty_status', models.CharField(default='Archived', max_length=20)),
                ('archived_at', models.DateTimeField(auto_now_add=True)),
                ('assignments_data', models.JSONField(blank=True, default=list)),
            ],
            options={
                'db_table': 'Archived_Faculty',
            },
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('faculty_id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('middle_initial', models.CharField(blank=True, max_length=10)),
                ('password', models.CharField(max_length=128)),
                ('faculty_status', models.CharField(choices=[('Continuing', 'Continuing'), ('Completed', 'Completed')], default='Continuing', max_length=20)),
                ('password_changed', models.BooleanField(default=False)),
                ('password_changed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Faculty',
            },
        ),
        migrations.CreateModel(
            name='FacultyAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program', models.CharField(choices=[('Computer Science', 'Computer Science'), ('Information Technology', 'Information Technology')], max_length=50)),
                ('year_section', models.CharField(max_length=20)),
                ('semester', models.CharField(choices=[('1st Semester', '1st Semester'), ('2nd Semester', '2nd Semester'), ('Summer', 'Summer')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='Faculty.Faculty')),
            ],
            options={
                'db_table': 'Faculty_Assignment',
                'unique_together': {('faculty', 'program', 'year_section', 'semester')},
            },
        ),
    ]
