# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0018_deposit_iss'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursereport',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coursereport',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]