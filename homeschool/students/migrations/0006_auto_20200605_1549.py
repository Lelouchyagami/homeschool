# Generated by Django 3.0.2 on 2020-06-05 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0005_auto_20200605_1549'),
        ('students', '0005_auto_20200605_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='grade_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schools.GradeLevel'),
        ),
        migrations.AlterField(
            model_name='student',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='schools.School'),
        ),
    ]