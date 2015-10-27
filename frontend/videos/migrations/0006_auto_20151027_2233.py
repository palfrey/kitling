# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0005_video_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='lastRetrieved',
            field=models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0)),
        ),
    ]
