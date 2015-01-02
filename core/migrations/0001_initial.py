# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AliasClassNames',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('raceclass', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LapTimes',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('racelap', models.SmallIntegerField()),
                ('raceposition', models.SmallIntegerField(null=True)),
                ('racelaptime', models.DecimalField(null=True, decimal_places=3, max_digits=6)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OfficialClassNames',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('raceclass', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RacerId',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('racerpreferredname', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SingleRaceDetails',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('racedata', models.CharField(max_length=200)),
                ('roundnumber', models.IntegerField(null=True)),
                ('racenumber', models.IntegerField(null=True)),
                ('racedate', models.DateTimeField(verbose_name='Date of the race')),
                ('uploaddate', models.DateTimeField(verbose_name='Date the race was uploaded')),
                ('racelength', models.IntegerField(verbose_name='Number of minutes for the race')),
                ('winninglapcount', models.IntegerField(verbose_name='Number of laps that won the race')),
                ('mainevent', models.SmallIntegerField(null=True)),
                ('maineventroundnum', models.SmallIntegerField(null=True)),
                ('maineventparsed', models.CharField(null=True, max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SingleRaceResults',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('carnum', models.SmallIntegerField(verbose_name='Car number for this race')),
                ('lapcount', models.SmallIntegerField(verbose_name='Number of laps they completed')),
                ('racetime', models.TimeField(null=True)),
                ('fastlap', models.DecimalField(null=True, decimal_places=3, max_digits=6)),
                ('behind', models.DecimalField(null=True, decimal_places=3, max_digits=6)),
                ('finalpos', models.SmallIntegerField(verbose_name='Final race position')),
                ('raceid', models.ForeignKey(to='core.SingleRaceDetails')),
                ('racerid', models.ForeignKey(to='core.RacerId')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SupportedTrackName',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('trackurl', models.URLField()),
                ('region', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrackName',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('trackname', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='supportedtrackname',
            name='trackkey',
            field=models.ForeignKey(to='core.TrackName'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singleracedetails',
            name='trackkey',
            field=models.ForeignKey(to='core.TrackName'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='laptimes',
            name='raceid',
            field=models.ForeignKey(to='core.SingleRaceDetails'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='laptimes',
            name='racerid',
            field=models.ForeignKey(to='core.RacerId'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='aliasclassnames',
            name='officialclass',
            field=models.ForeignKey(to='core.OfficialClassNames'),
            preserve_default=True,
        ),
    ]
