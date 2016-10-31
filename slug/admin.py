# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.forms.models import ModelChoiceField

from reversion.admin import VersionAdmin
from help.models import Instruction

from models import ObjectSlug
from organization.models import Organization


class ObjectSlugAdmin(VersionAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'content_type':
            ct_ids = []
            ct_ids.append(ContentType.objects.get_for_model(Organization).id)
            ct_ids.append(ContentType.objects.get_for_model(Instruction).id)
            queryset = ContentType.objects.filter(id__in=ct_ids)
            return ModelChoiceField(queryset)

        return super(ObjectSlugAdmin, self).formfield_for_foreignkey(db_field, request,
                                                                     kwargs)

    def save_model(self, request, obj, form, change):
        original_text = obj.object.slugifiable_text()
        obj.original_text = original_text
        obj.save()
        slug_str = obj.slug
        for code, lang in settings.LANGUAGES:
            if code == obj.language:
                continue
            try:
                old_slug = obj.object.slugs.get(slug=slug_str, language=code)
                if old_slug.pk != obj.object.slugs.latest(lang).pk:
                    # same slug existed but it's not the active (latest) slug
                    old_slug.delete()
                    raise ObjectSlug.DoesNotExist

                # @attention: case-sensitive comparison:
                if old_slug.slug != slug_str:
                    old_slug.slug = slug_str
                    old_slug.original_text = original_text
                    old_slug.save()  # update is enough, i guess
            except ObjectSlug.DoesNotExist:
                # creates language version of slug
                # but do not want it to be latest
                latest = obj.object.slugs.latest(lang=code)
                obj.object.slugs.create(slug=slug_str, language=code,
                                        original_text=original_text)

                latest.delete()
                latest.pk = None
                latest.save()

    list_filter = (('content_type', admin.RelatedOnlyFieldListFilter, ), 'added', )
    list_display = ('id', 'content_type', 'slug', 'language', 'object_id', 'object',
                    'added', )
    exclude = ('original_text', )
    search_fields = ('slug', 'content_type', )


admin.site.register(ObjectSlug, ObjectSlugAdmin)
