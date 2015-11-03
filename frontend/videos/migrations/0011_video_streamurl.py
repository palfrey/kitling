# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0010_auto_20151028_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='streamURL',
            field=models.CharField(max_length=2048, null=True),
        ),
    ]
