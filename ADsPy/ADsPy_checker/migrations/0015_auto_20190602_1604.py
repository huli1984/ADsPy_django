# Generated by Django 2.2 on 2019-06-02 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0014_auto_20190602_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysearch',
            name='job_timeout',
            field=models.CharField(default=900, max_length=9),
        ),
    ]