# Generated by Django 2.2 on 2019-11-06 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0022_auto_20191106_0108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mysearch',
            name='job_starts',
            field=models.CharField(default='now', max_length=5),
        ),
    ]