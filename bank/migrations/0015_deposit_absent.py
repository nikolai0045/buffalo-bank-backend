# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0014_auto_20170817_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='deposit',
            name='absent',
            field=models.BooleanField(default=False),
        ),
    ]
