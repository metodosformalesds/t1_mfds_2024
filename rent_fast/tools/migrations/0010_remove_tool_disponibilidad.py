# Generated by Django 5.1.2 on 2024-11-18 20:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0009_tool_disponibilidad'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tool',
            name='disponibilidad',
        ),
    ]
