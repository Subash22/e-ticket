# Generated by Django 4.0.5 on 2022-06-27 03:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='f_name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='l_name',
            new_name='last_name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='password',
        ),
    ]