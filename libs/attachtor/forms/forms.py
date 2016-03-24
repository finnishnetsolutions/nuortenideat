# coding=utf-8

from __future__ import unicode_literals

from django import forms

from ..models import Upload
from ..utils import get_upload_group_id, get_upload_token
from .fields import RedactorAttachtorFieldMixIn, UploadSignatureField


class FileUploadForm(forms.ModelForm):

    class Meta:
        model = Upload
        fields = ('file', )


class RedactorAttachtorFormMixIn(object):
    upload_signature_field = 'upload_ticket'

    def __init__(self, *args, **kwargs):
        upload_group_id = get_upload_group_id(kwargs.get('instance', None))
        kwargs.setdefault('initial', {})
        kwargs['initial'][self.upload_signature_field] =\
            upload_group_id + get_upload_token(upload_group_id)
        super(RedactorAttachtorFormMixIn, self).__init__(*args, **kwargs)
        self.fields[self.upload_signature_field] = UploadSignatureField()

        for f in self.fields.values():
            if isinstance(f, RedactorAttachtorFieldMixIn):
                f.upload_group_id = upload_group_id

    def save(self, commit=True):
        new = self.instance.pk is None
        if self.instance is not None:
            setattr(self.instance, '_attachtor_upload_group_id',
                    self.cleaned_data['upload_ticket'][:32])
        return super(RedactorAttachtorFormMixIn, self).save(commit=commit)
