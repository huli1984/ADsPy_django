# Generated by Django 2.2 on 2019-06-02 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0008_auto_20190531_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysearch',
            name='job_timeout_time',
            field=models.TimeField(default='00:00'),
            preserve_default=False,
        ),
    ]
