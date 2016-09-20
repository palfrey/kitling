# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0014_add_enabled_and_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(unique=True)),
                ('enabled', models.BooleanField(default=True)),
                ('working', models.BooleanField(default=False)),
                ('lastRetrieved', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0))),
                ('notes', models.CharField(max_length=1024, null=True, blank=True)),
            ],
        ),
    ]
