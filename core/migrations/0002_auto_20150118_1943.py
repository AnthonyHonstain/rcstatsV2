# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supportedtrackname',
            name='region',
        ),
        migrations.RemoveField(
            model_name='supportedtrackname',
            name='trackurl',
        ),
    ]
