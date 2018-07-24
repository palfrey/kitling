# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0016_video_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='name',
            field=models.CharField(default=b'', max_length=255),
        ),
    ]
