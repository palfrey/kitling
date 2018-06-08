# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0005_video_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='lastRetrieved',
            field=models.DateTimeField(default=timezone.make_aware(datetime.datetime(1970,1,1))),
        ),
    ]
