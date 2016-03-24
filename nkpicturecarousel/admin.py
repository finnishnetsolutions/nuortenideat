# coding: utf-8

from __future__ import unicode_literals

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext as _

from account.models import UserSettings
from .models import PictureCarouselSet, PictureCarouselImage


# Fixes no validation on unique_together when inserting.
class CarouselImageInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        cleaned_data = super(CarouselImageInlineFormset, self).clean()

        error_msg = forms.ValidationError(
            _("Et voi ladata kahta kieliversiota samasta kielestä.")
        )
        inline_forms = [
            form for form in self.forms if "language" in form.cleaned_data
        ]
        languages = [
            form.cleaned_data["language"]
            for form in self.forms if "language" in form.cleaned_data
        ]
        for form in inline_forms:
            if languages.count(form.cleaned_data["language"]) > 1:
                form.add_error("language", error_msg)

        return cleaned_data


class CarouselImageInLine(admin.StackedInline):
    model = PictureCarouselImage
    formset = CarouselImageInlineFormset
    min_num = 1

    def __init__(self, *args, **kwargs):
        super(CarouselImageInLine, self).__init__(*args, **kwargs)
        self.extra = len(UserSettings.LANGUAGE_CHOICES) - 1
        self.max_num = len(UserSettings.LANGUAGE_CHOICES)


@admin.register(PictureCarouselSet)
class CarouselSetAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    inlines = [CarouselImageInLine]
