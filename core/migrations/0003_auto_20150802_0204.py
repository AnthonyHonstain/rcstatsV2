# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150118_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singleracedetails',
            name='racedate',
            field=models.DateTimeField(verbose_name='Date of the race', db_index=True),
            preserve_default=True,
        ),
    ]
