# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0008_auto_20151028_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
