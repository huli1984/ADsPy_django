# Generated by Django 2.2 on 2019-06-02 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0009_mysearch_job_timeout_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mysearch',
            name='job_timeout_time',
        ),
        migrations.AddField(
            model_name='mysearch',
            name='insert_job_timeout',
            field=models.IntegerField(default=900),
        ),
    ]