# Generated by Django 2.2 on 2019-04-11 09:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysearch',
            name='result_field',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
