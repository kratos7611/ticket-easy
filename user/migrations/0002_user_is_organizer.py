# Generated by Django 3.2 on 2024-02-08 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_organizer',
            field=models.BooleanField(default=False),
        ),
    ]
