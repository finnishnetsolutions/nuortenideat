import re
from uuid import uuid4
from django.contrib.contenttypes import models as contenttypes
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.db.utils import IntegrityError
from django.utils.translation import ugettext_lazy as _, get_language
from django.conf import settings

# from ormcaching import models as ormcaching
from libs.multilingo.utils import MultiLangDict

from templatetags.slugify import slugify

from operator import attrgetter


class ObjectSlugManager(models.Manager):
    use_for_related_fields = True

    def latest(self, lang=None):
        if self.instance is None:
            raise Exception('This .latest() must only be used with a RelatedManager.')
        if lang:
            slugs = list(self.filter(language=lang).all())
        else:
            slugs = list(self.all())
        if not len(slugs):
            return None

        slugs.sort(key=attrgetter(self.model._meta.get_latest_by))
        return slugs[-1]


class ObjectSlug(models.Model):
    LANGUAGE_FINNISH = 'fi'
    LANGUAGE_SWEDISH = 'sv'
    LANGUAGE_CHOICES = (
        (LANGUAGE_FINNISH,   _("suomi")),
        (LANGUAGE_SWEDISH,   _("ruotsi")),
    )

    content_type = models.ForeignKey(contenttypes.ContentType)
    object_id = models.IntegerField()
    slug = models.SlugField(max_length=64)
    original_text = models.CharField(max_length=255, default=None)
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=5,
                                default=LANGUAGE_CHOICES[0][0])
    added = models.DateTimeField(auto_now_add=True)

    object = generic.GenericForeignKey('content_type', 'object_id')
    
    objects = ObjectSlugManager()
    # implied_objects = ormcaching.ImplicitCachingManager()

    def __unicode__(self):
        return u'%s #%d - %s' % (self.content_type, self.object_id, self.slug)

    # class Caching:
    #    cache_by = (('slug', 'content_type',), ('content_type', 'object_id',), )
    #    cache_timeout = 3*60*60

    class Meta:
        unique_together = (('content_type', 'slug', 'language'),)
        # manager.latest() overridden to be only used with RelatedManagers
        get_latest_by = 'id'


class SlugRelation(generic.GenericRelation):
    def __init__(self, *args, **kwargs):
        super(SlugRelation, self).__init__(ObjectSlug)

    def slugify_object(self, instance, created, **kwargs):
        lang_dict = self.prepare_multilang(instance.slugifiable_text())
        post_attribute = "_{}".format(uuid4().hex[:4])
        for lang, text_list in lang_dict.iteritems():
            for text in text_list:
                slug_str = slugify(text)
                try:
                    self.save_or_update_or_do_nothing(instance, slug_str, lang)
                except IntegrityError:
                    slug_str += post_attribute
                    self.save_or_update_or_do_nothing(instance, slug_str, lang)

    def save_or_update_or_do_nothing(self, instance, slug_str, lang):
        try:
            old_slug = instance.slugs.get(slug=slug_str, language=lang)
            if old_slug.pk != instance.slugs.latest(lang).pk:
                # same slug existed but it's not the active (latest) slug
                old_slug.delete()
                raise ObjectSlug.DoesNotExist

            clean_slug = re.sub(r'_[a-f0-9]+$', '', old_slug.slug)
            # @attention: case-sensitive comparison:
            if old_slug.slug not in (clean_slug, slug_str):
                old_slug.slug = slug_str
                old_slug.save()  # update is enough, i guess
        except ObjectSlug.DoesNotExist:
            instance.slugs.create(slug=slug_str, language=lang)

    def contribute_to_class(self, cls, name):
        super(SlugRelation, self).contribute_to_class(cls, name)
        signals.post_save.connect(self.slugify_object, sender=cls)

    def prepare_multilang(self, value):
        langs = {}
        for code, lang in settings.LANGUAGES:
            langs[code] = []
            if isinstance(value, MultiLangDict):
                # has language version
                if value[code]:
                    langs[code].extend(value.get_other_languages_values_list(code))
                langs[code].append(value[code])
            else:
                langs[code].append(value)
        return langs


class SlugifiedModel(models.Model):
    slugs = SlugRelation()

    def slugifiable_text(self):
        raise NotImplementedError
    
    # should return viewname for example: organization:detail
    # urls.py should also have a viewname with postfix _pk like organization:detail_pk
    # in case slug is not found
    def absolute_url_viewname(self):
        raise NotImplementedError

    def get_absolute_url(self, lang=None):
        if not lang:
            lang = get_language()
        slug = self.slugs.latest(lang)
        viewname = self.absolute_url_viewname()
        if not slug:
            kwargs = {'pk': self.pk}
            viewname += '_pk'
        else:
            kwargs = {'slug': slug.slug}
        return reverse(viewname, kwargs=kwargs)

    # get all slugs for content type
    def get_slug_list(self, id_list=None):
        ct_id = self.slugs.first().content_type_id
        params = {'content_type_id': ct_id}
        if id_list:
            params.update({'pk__in': id_list})
        qs = ObjectSlug.objects.filter(**params).order_by('pk')
        slug_list = {}
        for obj in qs:
            if obj.object_id not in slug_list:
                slug_list[obj.object_id] = {}
            slug_list[obj.object_id][obj.language] = obj

        return slug_list

    class Meta:
        abstract = True
