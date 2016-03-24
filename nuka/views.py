# coding=utf-8

from __future__ import unicode_literals

from operator import attrgetter
from random import randint

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count
from django.http.response import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.template import loader
from django.utils.translation import override
from django.views.generic.base import RedirectView, TemplateView, View
from nkpicturecarousel.models import PictureCarouselSet, PictureCarouselImage

from nuka.utils import chunks
from content.models import Idea, Initiative
from tagging.utils import tags_by_popularity


class PictureCarousel(object):
    picture_large = "ni_kuvakaruselli_{}_1140-2560_{}.jpg"
    picture_medium = "ni_kuvakaruselli_{}_940-2560_{}.jpg"
    picture_small = "ni_kuvakaruselli_{}_940x330_{}.jpg"
    picture_alt = ""

    def __init__(self, language):
        image_sets = PictureCarouselSet.objects.annotate(
            images_count=Count("images")
        ).filter(
            is_active=True,
            images_count__gt=0
        )
        if image_sets:
            image_sets_len = len(image_sets)
            if image_sets_len == 1:
                image_set = image_sets[0]
            else:
                random_number = randint(0, image_sets_len - 1)
                image_set = image_sets[random_number]

            try:
                image = image_set.images.get(language=language)
            except PictureCarouselImage.DoesNotExist:
                image = image_set.images.first()

            self.picture_large = image.image_large.url
            self.picture_medium = image.image_medium.url
            self.picture_small = image.image_small.url
            self.picture_alt = image.alt_text.capitalize()

        else:
            pic_choices = {
                "fi": ("ideoi", "kannata", "kommentoi"),
                "sv": ("föreslå", "gilla", "kommentera")
            }
            random_number = randint(0, 2)
            randomed_pic = pic_choices["fi"][random_number]

            self.picture_alt = pic_choices[language][random_number].capitalize()

            img_path = "nuka/img/karuselli kieliversiot/"
            self.picture_large = static(
                img_path + self.picture_large.format(randomed_pic, language)
            )
            self.picture_medium = static(
                img_path + self.picture_medium.format(randomed_pic, language)
            )
            self.picture_small = static(
                img_path + self.picture_small.format(randomed_pic, language)
            )


class PreFetchedObjectMixIn(object):
    obj_kwarg = 'obj'

    def get_object(self):
        return self.kwargs[self.obj_kwarg]


class FrontPageView(TemplateView):
    template_name = 'nuka/frontpage.html'
    initiatives_count = 12

    def get_context_data(self, **kwargs):
        context = super(FrontPageView, self).get_context_data(**kwargs)
        ideas = Idea.objects.filter(
            visibility=Initiative.VISIBILITY_PUBLIC
        ).order_by("-published")[:self.initiatives_count]
        ideas = ideas.prefetch_related('owners__settings', 'target_organizations')\
                     .defer('target_organizations__description')
        context["object_list"] = ideas
        context["initiatives_count"] = self.initiatives_count
        context["carousel"] = PictureCarousel(self.request.LANGUAGE_CODE)
        return context
    

class FrontPageLocaleRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            with override(language=self.request.user.settings.language):
                return reverse('frontpage')
        return reverse('frontpage')


class AllowedFileUploadExtensions(View):
    def get(self, request, **kwargs):
        return HttpResponse("\n".join(sorted(settings.FILE_UPLOAD_ALLOWED_EXTENSIONS)),
                            content_type='text/plain')


def error_page_not_found(request):
    return render(request, 'nuka/errors/404.html', status=404)