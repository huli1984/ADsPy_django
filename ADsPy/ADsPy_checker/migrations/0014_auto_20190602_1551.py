# Generated by Django 2.2 on 2019-06-02 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0013_auto_20190602_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysearch',
            name='job_timeout',
            field=models.CharField(max_length=9),
        ),
    ]