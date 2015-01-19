# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EasyUploadedRaces',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('racedetails', models.ForeignKey(to='core.SingleRaceDetails')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EasyUploaderPrimaryRecord',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('ip', models.IPAddressField()),
                ('filecount', models.IntegerField()),
                ('filecountsucceed', models.IntegerField()),
                ('uploadstart', models.DateTimeField(verbose_name='Datetime upload was started.')),
                ('uploadfinish', models.DateTimeField(null=True, verbose_name='Datetime the upload was completed.')),
                ('trackname', models.ForeignKey(null=True, to='core.TrackName')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EasyUploadRecord',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('origfilename', models.CharField(max_length=200)),
                ('filename', models.CharField(max_length=200, null=True)),
                ('ip', models.IPAddressField()),
                ('filesize', models.BigIntegerField()),
                ('filemd5', models.CharField(max_length=200, null=True)),
                ('uploadstart', models.DateTimeField(null=True, verbose_name='Date the file was uploaded.')),
                ('uploadfinish', models.DateTimeField(null=True, verbose_name='Date the file was finished uploaded and processed')),
                ('processed', models.BooleanField(default=False, verbose_name='We processed some or all of the file (still possible there was an error)')),
                ('errorenum', models.IntegerField(null=True)),
                ('trackname', models.ForeignKey(null=True, to='core.TrackName')),
                ('uploadrecord', models.ForeignKey(to='uploadresults.EasyUploaderPrimaryRecord')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='easyuploadedraces',
            name='upload',
            field=models.ForeignKey(to='uploadresults.EasyUploadRecord'),
            preserve_default=True,
        ),
    ]
