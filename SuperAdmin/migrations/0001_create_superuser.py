from django.db import migrations
from django.contrib.auth import get_user_model

def create_admin(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(username='sentinelsadmin').exists():
        User.objects.create_superuser(
            username='sentinelsadmin',
            email='admin@sentinels.com',
            password='sentinelsadmin123'
        )
        print("Created superuser: sentinelsadmin")
    else:
        print("Superuser sentinelsadmin already exists")

def reverse_create_admin(apps, schema_editor):
    User = get_user_model()
    User.objects.filter(username='sentinelsadmin').delete()

class Migration(migrations.Migration):
    initial = True  # Mark this as initial migration
    
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),  # Only depend on auth, not on itself
    ]

    operations = [
        migrations.RunPython(create_admin, reverse_create_admin),
    ]