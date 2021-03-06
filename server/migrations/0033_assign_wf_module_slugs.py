# Generated by Django 2.2.3 on 2019-07-30 12:35

from django.db import migrations


class Migration(migrations.Migration):
    """
    Assign a slug to all old WfModules.

    This is to transition from Olden Times, in which end-users referred to
    a WfModule by its ID. At the time this migration was applied, code had
    changed so no code would write any NULL-slug WfModule any more. So we
    need only assign a unique slug to each WfModule and then set the column
    NOT NULL.

    Unique slugs are easy to build: use the database ID.
    """

    dependencies = [("server", "0032_auto_20190729_0211")]

    operations = [
        migrations.RunSQL(
            [
                """
                UPDATE server_wfmodule
                SET slug = 'step-x' || id
                WHERE slug IS NULL
                """
            ],
            elidable=True,
        )
    ]
