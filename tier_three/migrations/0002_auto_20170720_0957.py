# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-20 13:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tier_three', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PassGoal',
            new_name='T3Goal',
        ),
        migrations.RenameModel(
            old_name='PassProfile',
            new_name='T3Profile',
        ),
        migrations.RenameModel(
            old_name='PassReport',
            new_name='T3Report',
        ),
    ]
