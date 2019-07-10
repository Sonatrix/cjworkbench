# Generated by Django 2.2.2 on 2019-06-18 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("server", "0019_workflow_last_viewed_at")]

    operations = [
        migrations.AddConstraint(
            model_name="wfmodule",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("next_update__isnull", True), ("auto_update_data", False)
                    ),
                    models.Q(
                        ("next_update__isnull", False), ("auto_update_data", True)
                    ),
                    _connector="OR",
                ),
                name="auto_update_consistency_check",
            ),
        )
    ]
