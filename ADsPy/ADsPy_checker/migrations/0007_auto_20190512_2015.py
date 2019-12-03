# Generated by Django 2.2 on 2019-05-12 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ADsPy_checker', '0006_mysearch_job_timeout'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mysearch',
            options={'ordering': ['-my_search_query']},
        ),
        migrations.RemoveField(
            model_name='mysearch',
            name='geolocation',
        ),
        migrations.RemoveField(
            model_name='mysearch',
            name='my_query',
        ),
        migrations.AlterField(
            model_name='mysearch',
            name='latandlong',
            field=models.CharField(default='Seppia', max_length=50),
        ),
        migrations.AlterField(
            model_name='mysearch',
            name='result_field',
            field=models.TextField(blank=True, null=True),
        ),
    ]