# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-11 15:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tier_three', '0003_auto_20170804_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='tthreereport',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
