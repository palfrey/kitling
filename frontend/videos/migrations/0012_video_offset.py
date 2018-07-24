# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0011_video_streamurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='offset',
            field=models.FloatField(default=0.0),
        ),
    ]
