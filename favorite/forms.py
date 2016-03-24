
# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from nuka.forms.widgets import Select2Multiple
from nuka.forms.fields import ModelMultipleChoiceField
from organization.models import Organization
from tagging.models import Tag
from account.models import User
from .models import Favorite


class UserFavoriteBaseForm(forms.ModelForm):

    def get_favorites(self, instance=None):
        ct = ContentType.objects.get_for_model(self.__class__.
                                               declared_fields['favorites'].queryset.
                                               model)
        return instance.favorites.filter(content_type=ct)

    def __init__(self, **kwargs):
        kwargs['initial'] = {'favorites': self.get_favorites(kwargs['instance']).
            values_list('object_id', flat=True)}
        super(UserFavoriteBaseForm, self).__init__(**kwargs)

    @transaction.atomic()
    def save(self):
        self.get_favorites(self.instance).delete()

        for item in self.cleaned_data['favorites']:
            Favorite(content_object=item, user=self.instance).save()


class UserFavoriteTagForm(UserFavoriteBaseForm):

    favorites = ModelMultipleChoiceField(label='', widget=Select2Multiple,
                                         queryset=Tag.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('favorites', )


class UserFavoriteOrganizationForm(UserFavoriteBaseForm):
    favorites = ModelMultipleChoiceField(label='', widget=Select2Multiple,
                                         queryset=Organization.objects.normal(), required=False)

    class Meta:
        model = User
        fields = ('favorites', )
