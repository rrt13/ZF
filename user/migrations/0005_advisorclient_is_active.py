# Generated by Django 3.2.10 on 2023-10-04 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_advisorclient'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisorclient',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
