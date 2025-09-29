from django.db import migrations
from django.contrib.auth import get_user_model

def create_admin(apps, schema_editor):
    User = get_user_model()
    # Only create the superuser if it doesn't already exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='sentinelsadmin',
            email='admin@sentinels.com',
            password='sentinelsadmin123'
        )

class Migration(migrations.Migration):

    dependencies = [
        ('SuperAdmin', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]
