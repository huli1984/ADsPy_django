# Generated by Django 2.2 on 2019-04-10 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MySearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('my_query', models.CharField(max_length=250)),
                ('timestamp_now', models.DateField(auto_now_add=True)),
                ('slug', models.SlugField()),
            ],
            options={
                'ordering': ['-my_query'],
            },
        ),
    ]
