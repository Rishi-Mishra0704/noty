# Generated by Django 5.0.2 on 2024-02-18 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sharednote',
            name='shared_from',
        ),
    ]
