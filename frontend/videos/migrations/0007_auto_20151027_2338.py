# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0006_auto_20151027_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='account',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='events',
            field=models.IntegerField(null=True),
        ),
    ]
