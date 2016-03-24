# coding=utf-8

from __future__ import unicode_literals
from functools import wraps

from uuid import uuid4
from django.core.exceptions import ValidationError

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from account.models import UserSettings


def _carousel_pic_path(size):
    @wraps(_carousel_pic_path)
    def inner(obj, name):
        return 'carousel/%d/%s_%s_%s.jpg' % (
            obj.carousel_set.pk, obj.language, size, uuid4().hex
        )
    return inner


class CarouselImageField(models.ImageField):
    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop("width")
        self.height = kwargs.pop("height")
        self.upload_to_size = kwargs.pop("upload_to_size")
        kwargs["upload_to"] = _carousel_pic_path(self.upload_to_size)
        super(CarouselImageField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(CarouselImageField, self).deconstruct()
        kwargs["width"] = self.width
        kwargs["height"] = self.height
        kwargs["upload_to_size"] = self.upload_to_size
        del kwargs["upload_to"]
        return name, path, args, kwargs

    def clean(self, value, model_instance):
        if self.width != value.width or self.height != value.height:
            raise ValidationError(_("Kuvan korkeus tai leveys ei vastaa pyydettyä."))
        return value


@python_2_unicode_compatible
class PictureCarouselSet(models.Model):
    name = models.CharField(_("Nimi"), max_length=100)
    is_active = models.BooleanField(_("aktiivinen"), default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("kuvakarusellin kuva")
        verbose_name_plural = _("kuvakarusellin kuvat")


@python_2_unicode_compatible
class PictureCarouselImage(models.Model):
    carousel_set = models.ForeignKey(PictureCarouselSet, related_name="images")

    language = models.CharField(
        _("kieli"), choices=UserSettings.LANGUAGE_CHOICES,
        max_length=5, default=UserSettings.LANGUAGE_CHOICES[0][0],
        help_text=_("Lisää kuvat vain kerran per kieli.")
    )

    image_large = CarouselImageField(
        _("iso"), help_text="2560x330 px (1140 px)",
        upload_to_size="1140-2560x330",
        width=2560, height=330
    )
    image_medium = CarouselImageField(
        _("keskikoko"), help_text="2560x330 px (940 px)",
        upload_to_size="940-2560x330",
        width=2560, height=330
    )
    image_small = CarouselImageField(
        _("pieni"), help_text="940x330 px",
        upload_to_size="940x330",
        width=940, height=330
    )

    alt_text = models.CharField(_("alt-teksti"), max_length=255)

    def __str__(self):
        choices = UserSettings.LANGUAGE_CHOICES
        value = next((v for k, v in choices if k == self.language), None)
        return value.encode("utf-8").capitalize()

    class Meta:
        unique_together = ("carousel_set", "language")
        verbose_name = _("kuvan kieliversio")
        verbose_name_plural = _("kuvan kieliversiot")
