# Generated by Django 3.2.8 on 2022-06-10 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BostonStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Boston Students',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('program', models.CharField(max_length=100)),
                ('semester', models.CharField(max_length=100)),
                ('shift', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='students/')),
            ],
            options={
                'verbose_name_plural': 'Students',
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_id', models.CharField(max_length=100)),
                ('checked_in', models.BooleanField(default=False)),
                ('checked_in_date', models.DateTimeField()),
                ('checked_out', models.BooleanField(default=False)),
                ('checked_out_date', models.DateTimeField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.student')),
            ],
            options={
                'verbose_name_plural': 'Tickets',
            },
        ),
    ]
