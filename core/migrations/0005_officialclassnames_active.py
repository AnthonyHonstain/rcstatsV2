# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_classemailsubscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='officialclassnames',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
