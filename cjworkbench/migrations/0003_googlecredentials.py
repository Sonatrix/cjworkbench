# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-24 16:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0008_alter_user_username_max_length"),
        ("cjworkbench", "0002_auto_20170803_0036"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoogleCredentials",
            fields=[
                (
                    "id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("credential", models.CharField(max_length=255, null=True)),
            ],
        )
    ]
