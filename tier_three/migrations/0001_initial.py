# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 03:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bank', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PassGoal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('goal', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PassProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.UserProfile')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.Student')),
            ],
        ),
        migrations.CreateModel(
            name='PassReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=4)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tier_three.PassProfile')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.CourseReport')),
            ],
        ),
        migrations.AddField(
            model_name='passgoal',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tier_three.PassProfile'),
        ),
    ]
