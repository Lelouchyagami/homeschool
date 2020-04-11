# Generated by Django 3.0.1 on 2020-04-11 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursetask',
            name='duration',
            field=models.PositiveIntegerField(default=60, help_text='The expected length of the task in minutes'),
            preserve_default=False,
        ),
    ]
