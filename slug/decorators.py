from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language

from models import ObjectSlug


def slug_to_object(model):
    def view_wrapper(func):
        def decorate_view(*args, **kwargs):
            lang = get_language()
            slug_str = kwargs.pop('slug')
            slug = get_object_or_404(
                ObjectSlug, content_type=ContentType.objects.get_for_model(model),
                slug=slug_str, language=lang)
            obj = slug.object
            if slug_str != slug.slug or obj.slugs.latest(lang).pk != slug.pk:
                return HttpResponsePermanentRedirect(obj.get_absolute_url())
            kwargs['obj'] = obj
            kwargs['pk'] = obj.pk
            return func(*args, **kwargs)
        return decorate_view
    return view_wrapper
