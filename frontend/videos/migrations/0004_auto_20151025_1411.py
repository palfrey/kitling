# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0003_auto_20151025_1355'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='name',
            field=models.CharField(default='foo', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='video',
            name='url',
            field=models.URLField(unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='feed',
            unique_together=set([('name', 'owner')]),
        ),
    ]
