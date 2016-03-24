# coding=utf-8

from __future__ import unicode_literals

import re
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from django.db.models import signals

from ..tasks import delete_uploaded_file


class UploadGroup(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.IntegerField(null=True)
    created = models.DateTimeField(default=timezone.now)

    content_object = GenericForeignKey()

    class Meta:
        unique_together = (('content_type', 'object_id', ), )


ext_regexp = re.compile(r'.+(\.[a-z0-9]{1,10})$', re.IGNORECASE)


def unique_path(instance, filename):
    match = ext_regexp.match(filename)
    ext = match.group(1) if match else ''
    uid = uuid4().hex
    return 'attachments/%s/%s/%s/%s' % (uid[0], uid[1], uid[2], uid[3:] + ext)


class Upload(models.Model):
    group = models.ForeignKey(UploadGroup, on_delete=models.CASCADE)
    file = models.FileField(max_length=255, upload_to=unique_path)
    original_name = models.CharField(max_length=255)
    size = models.BigIntegerField()
    created = models.DateTimeField(default=timezone.now)

    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                 on_delete=models.SET_NULL)


@receiver(signals.post_delete, sender=Upload)
def delete_file_when_upload_deleted(instance=None, **kwargs):
    delete_uploaded_file.apply_async(args=[instance.pk,
                                           instance.group_id,
                                           instance.file.name],
                                     countdown=10)
