# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-14 05:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0011_auto_20170714_0217'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='like_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]