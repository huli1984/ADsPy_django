# Generated by Django 2.2 on 2019-08-03 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0018_mysearch_job time scheduler'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mysearch',
            old_name='job time scheduler',
            new_name='job_starts',
        ),
    ]