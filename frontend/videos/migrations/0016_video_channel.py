# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0015_add_channel'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='channel',
            field=models.ForeignKey(default=None, blank=True, to='videos.Channel', null=True),
        ),
    ]
