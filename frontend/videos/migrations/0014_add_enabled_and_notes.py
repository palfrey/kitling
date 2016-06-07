# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0013_fix_nulls'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='video',
            name='notes',
            field=models.CharField(max_length=1024, null=True, blank=True),
        ),
    ]
