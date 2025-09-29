# SuperAdmin/migrations/0002_create_superuser.py

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

class Migration(migrations.Migration):

    dependencies = [
        ('SuperAdmin', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]
