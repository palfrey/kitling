# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0004_auto_20151025_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='hash',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
