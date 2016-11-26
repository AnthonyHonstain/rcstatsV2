# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_auto_20150118_1943'),
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
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('primaryrecord', models.ForeignKey(to='uploadresults.EasyUploaderPrimaryRecord')),
                ('trackname', models.ForeignKey(to='core.Track')),
                ('uploadrecord', models.ForeignKey(to='uploadresults.EasyUploadRecord')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
