# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-26 00:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0021_auto_20170906_1549'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['course_number', 'section_number']},
        ),
    ]
