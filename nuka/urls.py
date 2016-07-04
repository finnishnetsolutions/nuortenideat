# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url, handler404
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import RedirectView

from libs.djcontrib.utils.decorators import combo
from libs.moderation.helpers import auto_discover
from libs.permitter.decorators import check_perm

from nkmessages.views import FeedbackView
from content.views import UploadAttachmentView
from nkwidget.views import ShowWidgetView
from nuka.decorators import legacy_json_plaintext
from nuka.views import AllowedFileUploadExtensions, error_page_not_found

from .perms import IsAuthenticated
from . import views

auto_discover()

urlpatterns = patterns('',
    # Non-localized patterns
    url(r'^$', views.FrontPageLocaleRedirectView.as_view(), name='frontpage_redirect'),
    url(r'^api/kua/', include('kuaapi.urls', namespace='kuaapi')),

    url('^api/$', RedirectView.as_view(url='/api/open/0.1/', permanent=False)),  # HACK
    url(r'^api/open/', include('openapi.urls', namespace='openapi')),

) + i18n_patterns('',
    # Localized patterns
    url(r'^$', views.FrontPageView.as_view(), name='frontpage'),
    url(r'^kayttaja/', include('account.urls', namespace='account')),
    url(r'^hallinta/', include('nkadmin.urls', namespace='nkadmin')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('content.urls', namespace='content')),
    url(r'^organisaatiot/', include('organization.urls', namespace='organization')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog'),
    url(r'^kommentit/', include('nkcomments.urls', namespace='nkcomments')),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'^palaute/$', FeedbackView.as_view(), name="feedback"),
    url(r'', include('nkmoderation.urls', namespace='nkmoderation')),
    url(r'^tietoa-palvelusta/', include('help.urls', namespace='help')),
    url(r'^tiedotteet/', include('info.urls', namespace='info')),
    url(r'^kampanjat/', include('campaign.urls', namespace='campaign')),
    url(r'^suosikit/', include('favorite.urls', namespace='favorite')),
    url(r'^widget/', xframe_options_exempt(ShowWidgetView.as_view()), name="nkwidget"),
    url(r'^', include('survey.urls', namespace='survey')),
    url('^liitteet/laheta/(?P<upload_group_id>[a-f0-9]{32})'
        '(?P<upload_token>[a-f0-9]{32})/$',
        combo(check_perm(IsAuthenticated), legacy_json_plaintext)(
            UploadAttachmentView.as_view()
        ),
        name='attachtor_file_upload'),
    url('^liitteet/sallitut-paatteet/$', AllowedFileUploadExtensions.as_view(),
        name='allowed_file_upload_extensions')
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.STATIC_URL.startswith('http'):
    urlpatterns += staticfiles_urlpatterns('/static/')

handler404 = views.error_page_not_found
