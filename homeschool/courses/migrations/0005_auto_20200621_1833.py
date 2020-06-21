# Generated by Django 3.0.2 on 2020-06-21 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20200605_1549'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coursetask',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='coursetask',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=5, editable=False, verbose_name='order'),
            preserve_default=False,
        ),
    ]
