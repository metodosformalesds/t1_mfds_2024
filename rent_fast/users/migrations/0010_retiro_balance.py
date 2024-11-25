# Generated by Django 4.2.16 on 2024-11-19 21:36

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_direccion_colonia'),
    ]

    operations = [
        migrations.CreateModel(
            name='Retiro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('arrendador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retiros', to='users.arrendador')),
            ],
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saldo_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('arrendador', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='balance', to='users.arrendador')),
            ],
        ),
    ]
