# coding=utf-8

from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import get_language

from redactor.widgets import RedactorEditor

from ..utils import get_upload_token


class RedactorAttachtorWidget(RedactorEditor):
    init_js = '''<script type="text/javascript">
                    jQuery(document).ready(function(){
                        var $field = jQuery("#%s");
                        options = %s;
                        options.imageUploadErrorCallback =
                        options.fileUploadErrorCallback = function(json){
                            alert(json.error);
                        };
                        $field.redactor(options);
                    });
                 </script>
              '''

    def __init__(self, *args, **kwargs):
        super(RedactorAttachtorWidget, self).__init__(*args, **kwargs)
        self.upload_group_id = kwargs.pop('upload_group_id', None)

    def _get_upload_group_id(self):
        return self._upload_group_id

    def _set_upload_group_id(self, val):
        self._upload_group_id = val

    upload_group_id = property(_get_upload_group_id, _set_upload_group_id)

    def get_options(self):
        options = getattr(settings, 'REDACTOR', {}).copy()
        options.update(self.custom_options)
        upload_url = reverse('attachtor_file_upload', kwargs={
            'upload_group_id': self.upload_group_id,
            'upload_token': get_upload_token(self.upload_group_id)
        })
        if self.allow_file_upload:
            options.setdefault('fileUpload', upload_url)
        if self.allow_image_upload:
            options.setdefault('imageUpload', upload_url)
        options['lang'] = get_language()
        return json.dumps(options)
