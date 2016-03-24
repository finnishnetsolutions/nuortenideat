# coding=utf-8

from __future__ import unicode_literals

import logging

from celery.app import shared_task


logger = logging.getLogger(__package__)


@shared_task
def delete_uploaded_file(upload_id, group_id, filename):
    from .models import Upload
    try:
        Upload.objects.get(pk=upload_id, group_id=group_id)
    except Upload.DoesNotExist:
        Upload().file.storage.delete(filename)
        logger.info("Deleted upload #%d: %s", upload_id, filename)
    else:
        logger.warning("Upload #%d still exists in the database, "
                       "deletion of %s cancelled.",
                       upload_id, filename)
