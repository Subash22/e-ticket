# Generated by Django 4.0.5 on 2022-07-02 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_f_name_customuser_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='phone',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]