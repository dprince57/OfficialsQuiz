# Generated by Django 5.1.3 on 2024-11-28 19:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='publish_time',
        ),
    ]