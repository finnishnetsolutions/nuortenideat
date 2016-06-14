# coding=utf-8

from __future__ import unicode_literals
from django import forms
from django.contrib.admin.templatetags import admin_static
from django.contrib.admin.widgets import AdminFileWidget
from django.conf import settings


class CropWidget(object):

    def _media(self):
        js = [
            # "image_cropping/js/jquery.Jcrop.min.js",
            "image_cropping/image_cropping.js",
        ]
        js = [admin_static.static(path) for path in js]

        if settings.IMAGE_CROPPING_JQUERY_URL:
            js.insert(0, settings.IMAGE_CROPPING_JQUERY_URL)

        css = [
            # "image_cropping/css/jquery.Jcrop.min.css",
            "image_cropping/css/image_cropping.css",
        ]
        css = {'all': [admin_static.static(path) for path in css]}

        return forms.Media(css=css, js=js)

    media = property(_media)


class ImageCropWidget(AdminFileWidget, CropWidget):

    def get_attrs(self, image, name):
        width = image.width
        height = image.height
        return {
            'class': "crop-thumb",
            'data-thumbnail-url': image.url,
            'data-field-name': name,
            'data-org-width': width,
            'data-org-height': height,
            'data-max-width': width,
            'data-max-height': height,
        }

    def render(self, name, value, attrs=None):
        if not attrs:
            attrs = {}
        if value:
            attrs.update(self.get_attrs(value, name))
        print self.media
        return super(AdminFileWidget, self).render(name, value, attrs)
