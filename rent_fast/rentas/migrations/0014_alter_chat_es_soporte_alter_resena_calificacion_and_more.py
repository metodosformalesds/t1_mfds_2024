# Generated by Django 4.2.16 on 2024-11-19 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentas', '0013_merge_20241119_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='es_soporte',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='resena',
            name='calificacion',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=0),
        ),
        migrations.DeleteModel(
            name='Pago',
        ),
    ]