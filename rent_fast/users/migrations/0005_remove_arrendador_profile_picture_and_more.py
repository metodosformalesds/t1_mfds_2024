# Generated by Django 4.2.16 on 2024-10-30 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_arrendador_profile_picture_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='arrendador',
            name='profile_picture',
        ),
        migrations.RemoveField(
            model_name='arrendatario',
            name='profile_picture',
        ),
    ]