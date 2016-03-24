# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = patterns('',
    url('^1.0/initiative/(?P<nua_initiative_id>\d+)/status/create/$',
        csrf_exempt(views.CreateStatusApiView.as_view()),
        name='create_initiative_status')
)


if settings.KUA_API['simulation']:
    urlpatterns += patterns('',
        url('^kua-simulation/', include('kuaapi.simulation.urls',
                                        namespace='kuasimulation'))
    )

