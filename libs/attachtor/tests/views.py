# coding=utf-8

from __future__ import unicode_literals

from django.http.response import HttpResponse
from django.views.generic.edit import CreateView, UpdateView

from .forms import BlogForm
from .models import Blog


class BlogBaseView(object):
    form_class = BlogForm
    model = Blog

    def form_valid(self, form):
        form.save()
        return HttpResponse('success')

    def form_invalid(self, form):
        return HttpResponse('failure: %s' % form.errors)


class CreateBlogView(BlogBaseView, CreateView):
    pass


class UpdateBlogView(BlogBaseView, UpdateView):
    pass

