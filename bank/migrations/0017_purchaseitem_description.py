# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-17 22:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0016_auto_20170817_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
