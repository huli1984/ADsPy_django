# Generated by Django 2.2 on 2019-04-25 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0004_auto_20190425_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysearch',
            name='latandlong',
            field=models.CharField(default='Del Buono', max_length=50),
        ),
    ]
