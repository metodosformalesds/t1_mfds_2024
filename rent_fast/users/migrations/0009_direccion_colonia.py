# Generated by Django 5.1.2 on 2024-11-17 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_notificacion_herramienta'),
    ]

    operations = [
        migrations.AddField(
            model_name='direccion',
            name='colonia',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]