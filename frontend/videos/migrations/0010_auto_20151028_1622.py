# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0009_feed_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='videos',
            field=models.ManyToManyField(to='videos.Video', blank=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='extra',
            field=jsonfield.fields.JSONField(default={}, blank=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='hash',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
