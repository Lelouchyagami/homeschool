# Generated by Django 3.0.4 on 2020-04-03 22:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
