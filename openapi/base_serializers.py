 # coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.translation import override

from rest_framework import relations, serializers, pagination
from rest_framework.settings import api_settings
from rest_framework.utils.field_mapping import get_url_kwargs

from libs.multilingo.utils import MultiLangDict


class HyperlinkedRelatedFieldNamspaceMixIn(object):
    namespace = 'openapi'

    def get_url(self, obj, view_name, request, format):
        return super(HyperlinkedRelatedFieldNamspaceMixIn, self).get_url(
            obj, '%s:%s' % (self.namespace, view_name), request, format
        )


class MultilingualUrlField(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        kwargs['read_only'] = True
        kwargs['help_text'] = 'object detail URL for web browsers'
        self.url_generator = kwargs.pop('url_generator', 'get_absolute_url')
        super(MultilingualUrlField, self).__init__(*args, **kwargs)

    def get_attribute(self, instance):
        generator = getattr(instance, self.url_generator)
        base_url = settings.BASE_URL.rstrip('/')
        urls = MultiLangDict()

        for lang in dict(settings.LANGUAGES).keys():
            with override(language=lang):
                urls[lang] = '%s%s' %(base_url, generator())

        return urls

    def to_representation(self, value):
        return value


class HyperlinkedRelatedField(HyperlinkedRelatedFieldNamspaceMixIn,
                              relations.HyperlinkedRelatedField):
    pass


class HyperlinkedIdentityField(HyperlinkedRelatedFieldNamspaceMixIn,
                               relations.HyperlinkedIdentityField):
    pass


class HyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    """Use namespaced relatedfields."""

    _related_class = HyperlinkedRelatedField

    def get_fields(self):
        fields = super(HyperlinkedModelSerializer, self).get_fields()
        if api_settings.URL_FIELD_NAME in fields:
            # replace HyperlinkedIdentityField with one that's namespaceable
            fields[api_settings.URL_FIELD_NAME] = HyperlinkedIdentityField(
                help_text="object detail API URL",
                **get_url_kwargs(getattr(self.Meta, 'model'))
            )
        return fields


class MultilingualTextField(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', 'multilingual string')
        super(MultilingualTextField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        if not value:
            return MultiLangDict()
        if not isinstance(value, dict):
            return MultiLangDict(((settings.LANGUAGE_CODE, force_unicode(value)),))
        return value

    def to_internal_value(self, data):
        return data


class ReadOnlyIntegerField(serializers.ReadOnlyField,
                           serializers.IntegerField):
    pass


class NextPageField(pagination.NextPageField, serializers.URLField):
    pass


class PreviousPageField(pagination.PreviousPageField, serializers.URLField):
    pass


class PaginationSerializer(pagination.PaginationSerializer):
    """
    Field help_texts added for swagger docs.
    """
    count = ReadOnlyIntegerField(source='paginator.count',
                                 help_text="total object count")
    next = NextPageField(source='*', help_text="API URL for the next page of objects")
    previous = PreviousPageField(source='*',
                                 help_text="API URL for the previous page of objects")


class SerializerMethodIntegerField(serializers.SerializerMethodField,
                                   serializers.IntegerField):
    pass
