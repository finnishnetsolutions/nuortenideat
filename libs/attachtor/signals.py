# coding=utf-8

from __future__ import unicode_literals

import logging

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import signals

from .models import UploadGroup
from .utils import get_upload_group_id


logger = logging.getLogger(__package__)

field_registry = {}


def register(model_cls, field_name, extractor=None):
    global field_registry

    model_id = '%s.%s' % (model_cls._meta.app_label, model_cls._meta.model)

    def _post_save(instance=None, created=False, update_fields=None, **kwargs):
        html = ''

        upload_group_id = get_upload_group_id(instance)

        if created and hasattr(instance, '_attachtor_upload_group_id'):
            old_group_id = getattr(instance, '_attachtor_upload_group_id')
            try:
                old_group = UploadGroup.objects.get(pk=old_group_id)
            except UploadGroup.DoesNotExist:
                return
            else:
                with transaction.atomic():
                    upload_group = UploadGroup(
                        pk=upload_group_id,
                        content_object=instance
                    )
                    upload_group.save(force_insert=True)
                    old_group.upload_set.update(group_id=upload_group_id)
                    old_group.delete()
        elif created:
            return
        else:
            try:
                upload_group = UploadGroup.objects.get(pk=upload_group_id)
            except UploadGroup.DoesNotExist:
                return

        # let's collect all html content from registered fields so we can figure out
        # which uploads are still linked to
        for f, extractor in field_registry[model_id].iteritems():
            html += extractor(instance=instance, field_name=f)

        uploads_kept = 0

        for upload in upload_group.upload_set.all():
            if upload.file.name not in html:
                upload.delete()
            else:
                uploads_kept += 1

        if uploads_kept == 0:
            upload_group.delete()

    def _post_delete(instance=None, **kwargs):
        try:
            group = UploadGroup.objects.get(
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.pk
            )
        except UploadGroup.DoesNotExist:
            pass
        else:
            group.delete()

    new = model_id not in field_registry

    if extractor is None:
        extractor = model_cls._meta.get_field(field_name).extract_html_from_field

    field_registry.setdefault(model_id, {})
    if field_name in field_registry[model_id]:
        logger.warning("%s.%s double-registered for attachtor", model_cls, field_name)

    field_registry[model_id][field_name] = extractor

    if new:
        signals.post_save.connect(
            _post_save, sender=model_cls, weak=False,
            dispatch_uid='attachtor_post_save.%s' % model_id
        )

        signals.post_delete.connect(
            _post_delete, sender=model_cls, weak=False,
            dispatch_uid='attachtor_post_delete.%s' % model_id
        )
