# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth import views as auth
from django.utils.translation import ugettext as _
from account.perms import CanEditUser, CanViewUser
from account.pipeline import BACKEND_KEY_FB, BACKEND_KEY_GOOGLE

from libs.djcontrib.conf.urls import decorated_patterns
from libs.djcontrib.utils.decorators import combo
from libs.djcontrib.views.generic import FlashRedirectView
from libs.permitter.decorators import check_perm

from libs.djcontrib.utils.decorators import obj_by_pk

from .models import User
from . import views
from nuka.decorators import legacy_json_plaintext


urlpatterns = patterns('',
    url(r'^rekisteroidy/$', views.SignupView.as_view(), name='signup'),
    url(r'^rekisteroidy/facebook/$', views.SignupView.as_view(social=BACKEND_KEY_FB),
        name='signup_{}'.format(BACKEND_KEY_FB)),
    url(r'^rekisteroidy/google/$', views.SignupView.as_view(social=BACKEND_KEY_GOOGLE),
        name='signup_{}'.format(BACKEND_KEY_GOOGLE)),
    url(r'^valitse-rekisteroitymistapa/$', views.SignupChoicesView.as_view(),
        name='signup_choices'),
    url(r'^kirjaudu-sisaan/$', views.LoginView.as_view(), name='login'),
    url(r'^kirjaudu-ulos/$', views.LogoutView.as_view(), name='logout'),
    url(r'^aktivoi/$', views.ActivateView.as_view(), name='activate'),
    url(r'^aktivoi/facebook/$', views.ActivateView.as_view(social=BACKEND_KEY_FB),
        name='activate_{}'.format(BACKEND_KEY_FB)),
    url(r'^aktivoi/google/$', views.ActivateView.as_view(social=BACKEND_KEY_GOOGLE),
        name='activate_{}'.format(BACKEND_KEY_GOOGLE)),
    url(r'^vahvista-sahkoposti/(?P<token>\w{26,50})/$',
        views.EmailConfirmationView.as_view(),
        name='confirm_email'),
    url(r'^aktivoitu/$', views.ActivationDoneView.as_view(), name='activation_done'),
    url(r'(?P<user_id>\d+)/lista/', views.UserProfileIdeaList.as_view(),
        name='idea_list'),
    url(r'^nollaa-salasana/$', auth.password_reset, name='reset_password',
        kwargs={
            'template_name': 'account/user_reset_password.html',
            'email_template_name': 'account/email/password_reset.txt',
            'subject_template_name': 'account/email/password_reset_title.txt',
            'post_reset_redirect': 'account:password_reset_done',
        }),
    url(r'^nollaa-salasana/linkki-lahetetty/$', auth.password_reset_done,
        name='password_reset_done',
        kwargs={'template_name':
                'account/user_reset_password_link_sent.html'}),
    url(r'^nollaa-salasana/vahvista/(?P<uidb64>[0-9A-Za-z_\-]+)'
         '/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth.password_reset_confirm,
        name='password_reset_confirm',
        kwargs={
            'template_name': 'account/user_reset_password_confirm.html',
            'post_reset_redirect': 'account:password_reset_ready'
        }),
    url(r'^nollaa-salasana/valmis/$',
        FlashRedirectView.as_view(
            message=_("Salasanasi on vaihdettu. Voit nyt kirjautua sisään "
                      "käyttäen uutta salasanaasi."),
            pattern_name='account:login'
        ), name='password_reset_ready')
) + decorated_patterns('', combo(obj_by_pk(User, 'user_id'), check_perm(CanViewUser)),
    url(r'^(?P<user_id>\d+)/$',
        obj_by_pk(User, 'user_id')(views.UserProfileView.as_view()), name='profile'),
) + decorated_patterns('', combo(obj_by_pk(User, 'user_id'), check_perm(CanEditUser)),
    url(r'(?P<user_id>\d+)/asetukset/$', views.UserSettingsView.as_view(),
        name='settings'),
    url(r'(?P<user_id>\d+)/nayta-asetukset/',
        views.UserSettingsDetailView.as_view(),
        name='settings_detail'),
    url(r'(?P<user_id>\d+)/muokkaa-asetukset/',
        views.UserSettingsEditView.as_view(),
        name='settings_edit'),
    url(r'(?P<user_id>\d+)/asetukset/kuva/$', views.ProfilePictureView.as_view(),
        name='profile_picture'),
    url(r'(?P<user_id>\d+)/asetukset/kuva/muokkaa/$',
        legacy_json_plaintext(views.EditProfilePictureView.as_view()),
        name='edit_profile_picture'),
    url(r'(?P<user_id>\d+)/asetukset/kuva/rajaa/$',
        views.CropProfilePictureView.as_view(), name='crop_profile_picture'),
    url(r'(?P<user_id>\d+)/asetukset/kuva/poista/$',
        views.DeleteProfilePictureView.as_view(),
        name='delete_profile_picture'),
    url(r'(?P<user_id>\d+)/sulje/$',
        views.CloseAccountView.as_view(logout=True),
        name='close'),
    url(r'(?P<user_id>\d+)/muokkaa-ilmoitukset/$',
        views.NotificationOptionsEditView.as_view(),
        name='notification_options_edit'),
    url(r'(?P<user_id>\d+)/nayta-ilmoitukset/$',
        views.NotificationOptionsDetailView.as_view(),
        name='notification_options_detail'),
    url(r'(?P<user_id>\d+)/salasanan-vaihto/$', views.UserChangePasswordView.as_view(),
        name='password'),

    # Messages:
    url(r'^(?P<user_id>\d+)/viestit/$',
        views.MessagesListView.as_view(),
        name="messages"),
    url(r'^(?P<user_id>\d+)/viestit/(?P<message_id>\d+)/$',
        views.MessageDetailView.as_view(),
        name="show_message"),
    url(r'^(?P<user_id>\d+)/viestit/(?P<message_id>\d+)/vastaa/$',
        views.CreateMessageView.as_view(),
        name="respond_message"),
    url(r'^(?P<user_id>\d+)/viestit/uusi/$',
        views.CreateMessageView.as_view(),
        name="create_message"),
    url(r'^(?P<user_id>\d+)/viestit/uusi/(?P<initiative_id>\d+)/$',
        views.TransferIdeaMessageView.as_view(),
        name="transfer_idea_by_message"),
    url(r'^(?P<user_id>\d+)/viestit/taulu/$',
        views.MessagesListView.as_view(template_name="account/messages/list_table.html"),
        name="messages_table"),
    url(r'^(?P<user_id>\d+)/viestit/(?P<message_id>\d+)/poista/$',
        views.DeleteMessageView.as_view(),
        name="delete_message"),
)
