# coding=utf-8

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.forms.models import ModelForm

from libs.attachtor.forms.fields import UploadSignatureField
from libs.attachtor.forms.forms import RedactorAttachtorFormMixIn
from libs.multilingo.forms.fields import MultiLingualField

from .models import Topic
from nuka.forms.fields import MultilingualRedactorField


class TopicAdminForm(RedactorAttachtorFormMixIn, ModelForm):
    title = MultiLingualField(label=_("Otsikko"))
    description = MultilingualRedactorField(label=_("Sisältö"))
    upload_ticket = UploadSignatureField()

    class Media:
        js = {
            "redactor/langs/fi.js",
            "redactor/langs/sv.js"
        }


@admin.register(Topic)
class TopicAdmin(ModelAdmin):
    form = TopicAdminForm

