# coding=utf-8

from __future__ import unicode_literals

from django import http
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView

from .models import Campaign


class CampaignDetailFirstView(RedirectView):
    pattern_name = 'campaign:campaign_detail'

    def get_redirect_url(self, *args, **kwargs):
        obj = Campaign.objects.first()
        if obj is None:
            return None
        return super(CampaignDetailFirstView, self).get_redirect_url(pk=obj.pk)

    # Copied from RedirectView and overridden else condition.
    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        if url:
            if self.permanent:
                return http.HttpResponsePermanentRedirect(url)
            else:
                return http.HttpResponseRedirect(url)
        else:
            return render_to_response("campaign/campaign_list.html",
                                      RequestContext(request))


class CampaignDetailView(ListView):
    model = Campaign
    template_name = "campaign/campaign_list.html"

    def get_context_data(self, **kwargs):
        context = super(CampaignDetailView, self).get_context_data(**kwargs)
        context['selected_campaign'] = get_object_or_404(Campaign, pk=self.kwargs['pk'])
        return context
