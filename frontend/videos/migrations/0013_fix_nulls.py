# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0012_video_offset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='hash',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='streamURL',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),        
    ]
