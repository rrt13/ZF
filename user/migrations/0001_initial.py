# Generated by Django 3.2.21 on 2023-10-02 17:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('full_name', models.CharField(blank=True, max_length=150)),
                ('phone_number', models.CharField(max_length=10, unique=True)),
                ('role', models.CharField(choices=[('user', 'User'), ('advisor', 'Advisor'), ('admin', 'Admin')], default='user', max_length=10)),
                ('is_verified', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Users',
            },
        ),
    ]
