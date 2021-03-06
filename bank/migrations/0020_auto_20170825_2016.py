# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-26 00:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0019_auto_20170822_0737'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailySchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('courses', models.ManyToManyField(to='bank.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses', models.ManyToManyField(to='bank.Course')),
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
            model_name='schedule',
            name='time_slots',
            field=models.ManyToManyField(to='bank.TimeSlot'),
        ),
    ]
