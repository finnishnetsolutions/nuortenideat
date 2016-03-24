# coding=utf-8

from __future__ import unicode_literals

from django import forms

from libs.attachtor.forms.forms import RedactorAttachtorFormMixIn

from .models import Blog


class BlogForm(RedactorAttachtorFormMixIn, forms.ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'content',)
