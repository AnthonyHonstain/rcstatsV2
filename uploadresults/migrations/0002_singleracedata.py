# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150118_1943'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('uploadresults', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleRaceData',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('ip', models.IPAddressField()),
                ('filename', models.CharField(max_length=200)),
                ('data', models.TextField(verbose_name='The contents of the race file.')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(related_name='snippets', to=settings.AUTH_USER_MODEL)),
                ('trackname', models.ForeignKey(to='core.TrackName')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
