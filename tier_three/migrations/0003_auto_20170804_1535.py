# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 19:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tier_three', '0002_auto_20170720_0957'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='T3Goal',
            new_name='TThreeGoal',
        ),
        migrations.RenameModel(
            old_name='T3Profile',
            new_name='TThreeProfile',
        ),
        migrations.RenameModel(
            old_name='T3Report',
            new_name='TThreeReport',
        ),
    ]
