# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='lastRetrieved',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
