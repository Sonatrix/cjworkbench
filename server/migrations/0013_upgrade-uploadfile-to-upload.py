# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-31 18:24
from __future__ import unicode_literals

import json
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations


logger = logging.getLogger(__name__)


def move_uploaded_file(workflow, wf_module, uploaded_file):
    """
    Move files from /uuid.ext to /wf-1/wfm-2/uuid.ext.

    This helps delete leaked files and find problem files.
    """
    from server import minio

    bucket = uploaded_file.bucket
    old_key = uploaded_file.key
    if "/" in old_key:
        return

    new_key = f"wf-{workflow.id}/wfm-{wf_module.id}/{old_key}"

    logger.info(f"Move %s/%s to %s/%s", bucket, old_key, bucket, new_key)
    try:
        minio.copy(bucket, new_key, f"{bucket}/{old_key}")
        minio.remove(bucket, old_key)
    except minio.error.NoSuchKey:
        # old_key is missing. Two possibilities:
        #
        # 1. We're re-running this script after it failed once with
        #    atomic=True (which used to be set, by accident); the move already
        #    succeeded but the DB doesn't know it. In that case, continue
        #    because this error actually means, "all is well."
        # 2. The file didn't exist to begin with. In that case, write a blank
        #    file in its stead. That way the user will remark, "hey, Workbench
        #    ate my file!" instead of undefined behavior (which is worse).
        #    https://www.pivotaltracker.com/story/show/163336822
        if minio.exists(bucket, new_key):
            pass  # "all is well"
        else:
            # write an empty file
            minio.put_bytes(bucket, new_key, b"")
            uploaded_file.size = 0
            uploaded_file.save(update_fields=["size"])
    uploaded_file.key = new_key
    uploaded_file.save(update_fields=["key"])


def upgrade_wf_module(wf_module):
    """
    Convert a WfModule from 'uploadfile' to 'upload' module.

    This means changing its params and its module_id_name, then clearing its
    history. This is a destructive change.
    """
    # Clearing deltas is involved; Django Migrations can't do it. Import the
    # actual Workflow model, not the Migrations-generated model.
    from server.models import Workflow

    try:
        workflow = Workflow.objects.get(id=wf_module.tab.workflow_id)
    except ObjectDoesNotExist:
        # We deleted this module in a previous `upgrade_wf_module()` loop.
        # (That is, a workflow had 2+ upload modules and when we were upgrading
        # another one, we deleted this one.)
        logger.info(
            "WfModule %d was deleted in another iteration; skipping", wf_module.id
        )
        return

    # Clear undo history. ChangeParametersCommand and ChangeDataVersionCommands
    # already written to the database will break once we change the module.
    workflow.clear_deltas()
    # Clearing undo history might delete this wf_module! If it does, fail fast.
    try:
        wf_module.refresh_from_db()
    except ObjectDoesNotExist:
        logger.info("WfModule %d was deleted; skipping", wf_module.id)
        return

    # First, housekeeping: tidy uploaded_files filenames in s3
    for uploaded_file in wf_module.uploaded_files.all():
        move_uploaded_file(workflow, wf_module, uploaded_file)

    # Find the UUID of the currently-selected file.
    stored_at = wf_module.stored_data_version
    stored_object = wf_module.stored_objects.filter(stored_at=stored_at).first()
    if stored_object:
        # (old-style file select would set a StoredObject; its `metadata` TEXT
        # field looks like `[{"uuid":...,"name":...}]`.)
        #
        # I've checked: all `metadata` in production are encoded consistently
        uuid = json.loads(stored_object.metadata)[0]["uuid"]
        if wf_module.uploaded_files.filter(uuid=uuid).exists():
            logger.info("Found StoredObject UUID %s for wfm-%d", uuid, wf_module.id)
        else:
            logger.info(
                "StoredObject had invalid UUID %s for wfm-%d", uuid, wf_module.id
            )
            uuid = None  # and fall through
    else:
        uuid = None
    if uuid is None:
        # fallback to the latest UploadedFile
        uploaded_file = wf_module.uploaded_files.order_by("-created_at").first()
        if uploaded_file:
            uuid = uploaded_file.uuid
            logger.info("Found UploadedFile uuid %s for wfm-%d", uuid, wf_module.id)
        else:
            # Okay, there's no file.
            logger.info("No UUID for wfm-%d", wf_module.id)
            uuid = None

    # Update the `module_id_name` and `params`. `params.file` is the UUID of
    # the uploaded_file in question.
    wf_module.module_id_name = "upload"  # NEW module
    wf_module.params = {
        "file": uuid,  # may be None
        "has_header": wf_module.params["has_header"],
    }
    wf_module.save(update_fields=["module_id_name", "params"])


def upgrade_uploadfile_steps(apps, schema_editor):
    WfModule = apps.get_model("server", "WfModule")
    for wf_module in WfModule.objects.filter(module_id_name="uploadfile"):
        upgrade_wf_module(wf_module)


class Migration(migrations.Migration):
    """
    Convert all `uploadfile` modules into `upload` modules.

    This moves UploadedFile data on S3; finds the selected UUID; rewrites the
    WfModule's `module_id_name` and `params`; and clears the undo history
    (which is too difficult to preserve).

    Remember: UploadedFile is the stuff uploaded by the user. StoredObject is
    the "fetch result" table. The upload module doesn't fetch, so StoredObject
    was never the right place to store parsed data. Currently, we _cache_
    parsed data so we have no need for StoredObject at all. Instead, we point
    directly to UploadedFile: now the user gets API access to uploaded files.

    After this, StoredObject is completely useless on these modules.
    TODO delete their StoredObjects. (We keep them for now as a precaution.)
    TODO remove StoredObject.metadata, which was only ever to support the
    `uploadfile` module.
    """

    dependencies = [("server", "0012_merge_20190531_1440")]

    atomic = False

    operations = [migrations.RunPython(upgrade_uploadfile_steps, elidable=True)]
