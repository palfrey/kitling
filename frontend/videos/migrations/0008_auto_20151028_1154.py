# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0007_auto_20151027_2338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='account',
        ),
        migrations.RemoveField(
            model_name='video',
            name='events',
        ),
        migrations.AddField(
            model_name='video',
            name='extra',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
