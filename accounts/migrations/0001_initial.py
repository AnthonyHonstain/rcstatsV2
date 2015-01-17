# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import userena.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('mugshot', easy_thumbnails.fields.ThumbnailerImageField(help_text='A personal image displayed in your profile.', verbose_name='mugshot', blank=True, upload_to=userena.models.upload_to_mugshot)),
                ('privacy', models.CharField(help_text='Designates who can view your profile.', default='registered', max_length=15, choices=[('open', 'Open'), ('registered', 'Registered'), ('closed', 'Closed')], verbose_name='privacy')),
                ('user', models.OneToOneField(related_name='my_profile', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'permissions': (('view_profile', 'Can view profile'),),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
