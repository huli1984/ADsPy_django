# Generated by Django 2.2 on 2019-11-06 00:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0023_auto_20191106_0109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysearch',
            name='job_starts',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
