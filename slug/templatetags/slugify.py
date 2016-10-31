from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django import template

import re

register = template.Library()


def slugify(value):
    # just like django.template.defaultfilters.slugify, but does not call .lower()
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    return mark_safe(re.sub('[-\s]+', '-', value))
slugify.is_safe = True
slugify = stringfilter(slugify)


@register.simple_tag(takes_context=True)
def get_slug(context, obj, slug_list, language, asvar):
    context[asvar] = slug_list[obj.pk][language].slug
    return ''

