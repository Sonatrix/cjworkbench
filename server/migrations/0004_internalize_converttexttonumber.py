# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-11 21:22
from __future__ import unicode_literals

from django.db import migrations


def nix_code_from_minio(apps, schema_editor):
    from cjwstate import minio

    # Delete from S3
    try:
        minio.remove_recursive(minio.ExternalModulesBucket, "extract-numbers/")
    except minio.error.NoSuchBucket:
        pass  # we're unit-testing and the bucket doesn't exist


class Migration(migrations.Migration):
    """
    Internalize "converttexttonumber" module.

    Prior to this, users on production used an external module,
    'extract-numbers'. When we introduced number type formats, we started
    requiring conversions (as quick fixes) ... meaning Workbench is married to
    these converters.

    "Convert text to number" is the most important converter. We had to rename
    it so it would be compatible with the internal-module system.
    """

    dependencies = [("server", "0003_nix_external_convert_to_text")]

    operations = [
        migrations.RunSQL(
            [
                """
            UPDATE server_wfmodule
            SET module_id_name = 'converttexttonumber'
            WHERE module_id_name = 'extract-numbers'
            """,
                """
            DELETE FROM server_moduleversion
            WHERE id_name = 'extract-numbers'
            """,
            ],
            elidable=True,
        ),
        migrations.RunPython(nix_code_from_minio, elidable=True),
    ]
