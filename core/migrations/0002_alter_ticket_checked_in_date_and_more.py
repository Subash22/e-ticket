# Generated by Django 4.0.5 on 2022-06-10 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='checked_in_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='checked_out_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
