# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from libs.djcontrib.conf.urls import decorated_patterns
from libs.djcontrib.utils.decorators import combo
from openapi.decorators import swagger_content_type_hack, swagger_api_description_hack

from .routers import router


urlpatterns = patterns('',
    url('^$', RedirectView.as_view(url='/api/open/%s/' % settings.OPEN_API['version'],
                                   permanent=False), name='root'),
    url('^0.1/', include(router.urls))
) + decorated_patterns('', combo(swagger_content_type_hack, swagger_api_description_hack),
    url(r'^docs/', include('rest_framework_swagger.urls'))
)
