# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django import forms
from libs.attachtor.forms.forms import RedactorAttachtorFormMixIn
from libs.multilingo.forms.fields import MultiLingualField

from .models import Organization


class OrganizationAdminForm(RedactorAttachtorFormMixIn, forms.ModelForm):
    name = MultiLingualField(label=_("Nimi"))


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    form = OrganizationAdminForm
    list_display = ('name', 'type', 'is_active')


