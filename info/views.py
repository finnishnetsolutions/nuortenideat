# coding=utf-8

from __future__ import unicode_literals
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView

from .models import Topic


class TopicDetailFirst(RedirectView):
    permanent = False
    pattern_name = 'info:topic_detail'

    def get_redirect_url(self, *args, **kwargs):
        obj = Topic.objects.first()
        if obj is None:
            raise Http404()
        return super(TopicDetailFirst, self).get_redirect_url(pk=obj.pk)


class TopicDetail(ListView):
    model = Topic
    template_name = 'info/topic_list.html'

    def get_context_data(self, **kwargs):
        context = super(TopicDetail, self).get_context_data(**kwargs)
        context['selected_topic'] = get_object_or_404(
            Topic, pk=self.kwargs['pk'])
        return context