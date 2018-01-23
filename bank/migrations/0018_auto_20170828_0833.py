# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 08:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0017_auto_20170822_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailySchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('hour', models.CharField(max_length=20)),
                ('num_bucks', models.IntegerField(default=1)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='grade',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='courses',
            field=models.ManyToManyField(to='bank.Course'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='time_slots',
            field=models.ManyToManyField(to='bank.TimeSlot'),
        ),
        migrations.AddField(
            model_name='dailyschedule',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.Schedule'),
        ),
    ]