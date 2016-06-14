# coding=utf-8

from __future__ import unicode_literals

from collections import OrderedDict
from easy_thumbnails.files import get_thumbnailer
import requests
import re
import logging
from datetime import timedelta
from random import randint
from urllib2 import urlopen

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.template.defaultfilters import date
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.views import generic
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from account.models import NotificationOptions, UserSettings
from actions import lists
from actions.models import Action
from cropping.views import CropPictureView, EditCroppablePictureView

from libs.djcontrib.views.generic import MultiModelFormView

from account.forms import EditProfilePictureForm, MessageForm, UserProfileIdeaListForm, \
    UsernameForm, NotificationOptionsForm, PasswordChangeFormWithValidation, \
    CropProfilePictureForm
from content.models import Initiative, Idea, Question
from content.perms import CanSeeAllInitiatives

from .forms import EmailConfirmationForm, LoginForm, UserForm, UserSignUpForm, \
    UserActivateForm, UserSettingsEditForm
from libs.permitter.tests.perms import IsAuthenticated
from .models import User
from nkcomments.models import CustomComment
from nkmessages.models import Message
from nkvote.models import Vote
from nkvote.utils import get_voted_objects
from nuka.utils import send_email
from smslog.models import SentTxtMessages

# Get an instance of a logger
logger = logging.getLogger(__name__)


def profile_base_context(user):
    context = dict()
    context["ideas_count"] = user.initiatives.all().count()
    context["questions_count"] = Question.objects.filter(owners__in=(user,)).count()
    context["comments_count"] = CustomComment.objects.filter(user_id=user.pk).count()
    return context


class SignupChoicesView(TemplateView):
    template_name = 'account/signup_choices.html'


class SignupView(MultiModelFormView):
    template_name = 'account/signup.html'
    form_classes = (
        ('user', UserForm),
        ('usersettings', UserSignUpForm),
    )
    confirmation_email_template = 'account/email/confirm_signup.txt'
    confirmation_sms_template = 'account/sms/confirm_signup.txt'

    facebook = False

    def form_invalid(self):
        messages.error(self.request, _("Täytä kaikki pakolliset kentät."))
        return super(SignupView, self).form_invalid()

    @transaction.atomic()
    def form_valid(self):
        self.save_forms()

        # set default notifications
        user_settings = self.objects['usersettings']
        user_settings.message_notification = True
        user_settings.save()

        for o in lists.NOTIFICATION_OPTIONS:
            if o['group'] == Action.GROUP_ALL:
                ct = ContentType.objects.get_for_model(o['model'],
                                                       for_concrete_model=False)
                a_obj = NotificationOptions.objects.create(
                    user=self.objects['user'],
                    content_type=ct,
                    role=o['role'],
                    action_type=o['action_type'],
                    action_subtype=o['action_subtype'],
                    notify_at_once=True,
                )
                a_obj.save()

        if not self.facebook:
            return HttpResponseRedirect(reverse('account:activate'))
        else:
            return HttpResponseRedirect(reverse('account:activate_facebook'))

    def presave_usersettings(self, obj):
        """Link ``UserSettings`` to ``User`` before attempting to save."""
        obj.user = self.objects['user']

    def postsave(self):
        """``User`` and ``UserSettings`` have been saved, send the activation message."""
        user = self.objects['user']

        pin_code = self.generate_pincode()
        confirmation_method = self.forms['usersettings'].cleaned_data['confirmation_method']
        if confirmation_method == UserSignUpForm.CONFIRMATION_CHOICE_EMAIL:
            self.send_confirmation_email(user, pin_code)
        else:
            self.send_confirmation_sms(user, pin_code)

        self.request.session['sign_up'] = {'pin_code': pin_code, 'retry': 5,
                                           'user_id': user.pk}

        # Save the profile picture from Facebook, if chosen to.
        if self.facebook and self.request.POST["facebook_pic"] == "yes":
            facebook_id = self.request.session.get("fb_id")
            url = "http://graph.facebook.com/{0}/picture?type=large".format(facebook_id)
            picture = urlopen(url).read()
            user.settings.picture.save(
                user.username + "-social.jpg",
                ContentFile(picture),
                save=True
            )

    def send_confirmation_email(self, user, pin_code):
        activation_link = settings.BASE_URL + reverse(
            'account:confirm_email', kwargs={
                'token': EmailConfirmationForm.create_token(user)
            }
        )
        message = render_to_string(self.confirmation_email_template,
                                   {'activation_link': activation_link, 'pin_code': pin_code})
        mail.send_mail(_("Vahvista sähköpostiosoitteesi"), message, None,
                       [user.settings.email, ])

    def send_confirmation_sms(self, user, pin_code):
        message = render_to_string(self.confirmation_sms_template,
                                   {'pin_code': pin_code})
        if settings.SMS['enabled'] is True:
            today = timezone.now().date()
            resp = requests.get(settings.SMS['gateway'], params={
                'numero': user.settings.phone_number,
                'avain': today.day * today.month * today.year,
                'viesti': message.encode('latin-1'),
                'lahiosoite': 'PL 7260',
                'postitmp': '01051 LASKUT',
                'klinikka': 'Oikeusministeriö'.encode('latin-1'),
                'ohjelma': 'Nuorten ideat',
                'originator': _('NuortenIdeat')
            })

            if not 'OK' in resp.content:
                raise Exception("Tekstiviestin lähetys epäonnistui.")
            else:
                SentTxtMessages.create_and_save(user.settings.phone_number)
        else:
            print pin_code
            print user.settings.phone_number

    def generate_pincode(self):
        return '%04d' % randint(1, 9999)

    def get_usersettings_initial(self):
        if self.facebook:
            return {
                "email": self.request.session.get("fb_email"),
                "first_name": self.request.session.get("fb_first_name"),
                "last_name": self.request.session.get("fb_last_name"),
            }
        else:
            try:
                del self.request.session["fb_email"]
                del self.request.session["fb_first_name"]
                del self.request.session["fb_last_name"]
            except KeyError:
                pass

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        context["facebook"] = self.facebook
        context["facebook_id"] = self.request.session.get("fb_id")
        return context


class ActivateView(generic.FormView):
    template_name = 'account/signup_activation.html'
    form_class = UserActivateForm
    facebook = False

    def dispatch(self, request, *args, **kwargs):
        if 'sign_up' not in request.session:
            messages.error(request, _('Istunto vanhentunut'))
            return redirect('account:signup')
        return super(ActivateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        sign_up_data = self.request.session['sign_up']
        kwargs = super(ActivateView, self).get_form_kwargs()
        kwargs.update({
            'pin_code': sign_up_data['pin_code'],
            'retry': sign_up_data['retry']
        })

        return kwargs

    def send_email_notification(self, user):
        send_email(
            _("Käyttäjätili avattu."),
            'account/email/account_created.txt',
            {'user': user},
            [user.settings.email],
            user.settings.language
        )

    def form_invalid(self, form):
        if form.retries_used is True:
            user = User.objects.get(pk=self.request.session['sign_up']['user_id'])
            user.delete()
            messages.error(self.request, _('Aktivointiyritykset käytetty. Rekisteröidy uudelleen.'))
            return redirect('account:signup')
        self.request.session['sign_up']['retry'] -= 1
        self.request.session.save()
        return super(ActivateView, self).form_invalid(form)

    def form_valid(self, form):
        user = User.objects.get(pk=self.request.session['sign_up']['user_id'])
        user.status = User.STATUS_ACTIVE
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.save()
        self.send_email_notification(user)
        login(self.request, user)
        # TODO: logging configuration
        logger.info('User %s logged in. IP: %s', user.username,
                    self.request.META['REMOTE_ADDR'])
        if self.facebook:
            return redirect("social:complete", "facebook")
        else:
            return TemplateResponse(self.request, 'account/signup_activated.html',
                                    {'object': user})


class ActivationDoneView(generic.TemplateView):
    template_name = "account/signup_activated.html"

    def get_context_data(self, **kwargs):
        context = super(ActivationDoneView, self).get_context_data(**kwargs)
        context["object"] = self.request.user
        return context


class LogoutView(generic.RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        messages.success(
            self.request,
            ' '.join([
                _("Sinut on kirjattu ulos palvelusta."),
                _("Jos olet käyttänyt Facebook-kirjautumista, "
                  "muista kirjautua ulos myös Facebookista.")
            ])
        )
        return reverse('frontpage')


class EmailConfirmationView(generic.FormView):
    form_class = EmailConfirmationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(data=kwargs)
        if form.is_valid():
            form.save()
            return TemplateResponse(request, 'account/email_confirmed.html')
        else:
            return TemplateResponse(request, 'account/email_confirmation_failed.html',
                                    {'form': form})


class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = 'account/login.html'

    def form_valid(self, form):
        user = form.get_user()
        last_login = user.last_login
        login(self.request, user)
        if (last_login - user.joined) < timedelta(seconds=3):
            messages.success(self.request, _("Tervetuloa Nuortenideat.fi palveluun!"))
        else:
            messages.success(self.request, _("Tervetuloa! Käytit palvelua viimeksi %s.") %
                             date(last_login, 'DATETIME_FORMAT'))

        logger.info('User %s logged in. IP: %s', user.username,
                    self.request.META['REMOTE_ADDR'])

        if 'next' in self.request.GET:
            return HttpResponseRedirect(self.request.GET['next'])
        return redirect(reverse('account:profile',
                                kwargs={'user_id': user.pk}))

    def form_invalid(self, form):
        logger.info('Invalid login try for username %s. IP %s',
                    form.cleaned_data['username'], self.request.META['REMOTE_ADDR'])
        return super(LoginView, self).form_invalid(form)


class InlineUpdateView(UpdateView):
    def form_valid(self, form):
        super(InlineUpdateView, self).form_valid(form)
        return JsonResponse({'success': True,
                             'next': self.get_success_url()})


class ExistingUserMixIn(object):
    def get_object(self, queryset=None):
        return self.kwargs['obj']


class UserSettingsMixIn(object):
    def get_object(self, queryset=None):
        return self.kwargs['obj'].settings


class EditProfilePictureView(UserSettingsMixIn, InlineUpdateView,
                             EditCroppablePictureView):
    template_name = 'account/profile_picture_form.html'
    form_class = EditProfilePictureForm


class CropProfilePictureView(UserSettingsMixIn, InlineUpdateView, CropPictureView):
    form_class = CropProfilePictureForm


class ProfilePictureView(ExistingUserMixIn, DetailView):
    template_name = 'account/user_settings_picture.html'


class DeleteProfilePictureView(View):
    def delete(self, request, **kwargs):
        obj = get_object_or_404(User, pk=kwargs['user_id'])
        obj.settings.original_picture.delete()
        obj.settings.picture.delete()
        obj.settings.cropping = ''
        obj.settings.save()

        return JsonResponse({'success': True,
                             'next': reverse('account:profile_picture',
                                             kwargs={'user_id': obj.pk})})

    def post(self, request, **kwargs):
        return self.delete(request, **kwargs)


class UserProfileMixin(object):
    def get_initiatives(self):
        initiatives = Initiative.objects.filter(owners__in=(self.get_object(),),)
        if not CanSeeAllInitiatives(
            request=self.request, obj=self.get_object()
        ).is_authorized():
            if IsAuthenticated(request=self.request).is_authorized():
                initiatives = initiatives.filter(
                    Q(visibility=Initiative.VISIBILITY_PUBLIC)
                    | Q(owners__in=(self.request.user, ))
                )
            else:
                initiatives = initiatives.filter(visibility=Initiative.VISIBILITY_PUBLIC)
        return initiatives.order_by('-pk')


class UserProfileView(UserProfileMixin, generic.DetailView):
    pk_url_kwarg = 'user_id'
    template_name = 'account/user_profile.html'
    form_class = UserProfileIdeaListForm

    def get_object(self, queryset=None):
        return self.kwargs['obj']

    def get_context_data(self, **kwargs):
        kwargs = super(UserProfileView, self).get_context_data(**kwargs)
        user = self.get_object()
        initiatives = kwargs['initiatives'] = self.get_initiatives()

        kwargs['voted_ideas'] = get_voted_objects(self.request, initiatives, Idea)
        kwargs['ideas_count'] = initiatives.exclude(
            polymorphic_ctype_id=ContentType.objects.get_for_model(Question).pk
        ).count()
        kwargs['questions_count'] = initiatives.exclude(
            polymorphic_ctype_id=ContentType.objects.get_for_model(Idea).pk
        ).count()
        kwargs['comments_count'] = CustomComment.objects.filter(
            user_id=user.pk).count()
        kwargs["summary"] = True
        kwargs['form'] = self.form_class
        kwargs['is_public_profile'] = False if self.request.user == user else True
        return kwargs


class UserProfileIdeaList(UserProfileMixin, TemplateView):
    template_name = 'account/user_profile_idea_list.html'

    def get_object(self, **kwargs):
        return User.objects.get(pk=self.kwargs['user_id'])

    def get_context_data(self, *args, **kwargs):
        context = super(UserProfileIdeaList, self).get_context_data()
        context['ct_natural_key'] = self.request.GET['ct_natural_key']
        context['object'] = self.get_object()
        if not re.match('^([a-z])+\.([a-z])+$', context['ct_natural_key']):
            context['obj_list'] = self.get_non_favorite_initiatives(
                context['ct_natural_key'])
            context['ct_natural_key'] = None
        return context

    def get_non_favorite_initiatives(self, mode):
        if mode:
            id_list = list(CustomComment.objects.filter(user_id=self.get_object().pk).
                           values_list('object_pk', flat=True))
            id_list.extend(Vote.objects.filter(voter__user_id=self.get_object().pk).
                           values_list('object_id', flat=True))
            initiatives = Initiative.objects.filter(pk__in=id_list).distinct()

            if not CanSeeAllInitiatives(
                request=self.request, obj=self.get_object()
            ).is_authorized():
                if IsAuthenticated(request=self.request).is_authorized():
                    initiatives = initiatives.filter(
                        Q(visibility=Initiative.VISIBILITY_PUBLIC)
                        | Q(owners__in=(self.request.user, ))
                    )
                else:
                    initiatives = initiatives.filter(
                        visibility=Initiative.VISIBILITY_PUBLIC).order_by('-pk')
        else:
            initiatives = self.get_initiatives()
        return initiatives


class UserSettingsView(generic.DetailView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'account/user_settings.html'

    def get_context_data(self, **kwargs):
        # TODO: Initialize forms in OrderedDict()
        kwargs['forms'] = OrderedDict()
        kwargs["forms"]["user"] = UsernameForm(
            instance=self.get_object(),
            disable_helptext=True
        )
        kwargs["forms"]["usersettings"] = UserSettingsEditForm(
            instance=self.get_object().settings
        )

        kwargs['forms']['notification_options'] = NotificationOptionsForm(
            instance=self.get_object())
        return kwargs


class UserSettingsEditView(MultiModelFormView):
    template_name = 'account/user_settings_edit.html'
    form_classes = (
        ("user", UsernameForm),
        ("usersettings", UserSettingsEditForm)
    )

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['user_id'])

    def get_user_form_kwargs(self, kwargs):
        kwargs["instance"] = self.get_object()
        return kwargs

    def get_usersettings_form_kwargs(self, kwargs):
        kwargs["instance"] = self.get_object().settings
        return kwargs

    def get_success_url(self):
        return reverse('account:settings_detail', kwargs={
            'user_id': self.get_object().pk})

    def form_valid(self):
        self.save_forms()
        return JsonResponse({'success': True, 'next': self.get_success_url()})


class UserSettingsDetailView(MultiModelFormView):
    template_name = 'account/user_settings_detail.html'
    form_classes = (
        ("user", UsernameForm),
        ("usersettings", UserSettingsEditForm)
    )

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['user_id'])

    def get_user_form_kwargs(self, kwargs):
        kwargs["instance"] = self.get_object()
        kwargs["disable_helptext"] = True
        return kwargs

    def get_usersettings_form_kwargs(self, kwargs):
        kwargs["instance"] = self.get_object().settings
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(UserSettingsDetailView, self).get_context_data(**kwargs)
        context["object"] = self.get_object()
        return context


class UserChangePasswordView(generic.UpdateView):
    template_name = 'account/user_change_password.html'
    form_class = PasswordChangeFormWithValidation

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs['user_id'])

    def get_form(self, form_class):
        return form_class(self.get_object(), data=self.request.POST or None)

    def get_success_url(self):
        messages.success(self.request, _("Salasanasi on vaihdettu. Käytä seuraavan "
                                         "kirjautumisen yhteydessä uutta salasanaasi."))
        return reverse('account:settings', kwargs={'user_id': self.get_object().pk})

    def form_invalid(self, form):
        messages.error(self.request, _("Virhe. Tarkista lomakkeen tiedot."))
        return super(UserChangePasswordView, self).form_invalid(form)


class CloseAccountView(generic.View, generic.detail.SingleObjectMixin):
    model = User
    pk_url_kwarg = "user_id"
    http_method_names = ["post"]
    redirect_url = reverse_lazy("frontpage")
    logout = False

    def send_email_notification(self, user):
        send_email(
            _("Käyttäjätilisi on suljettu."),
            'account/email/account_closed.txt',
            {'user': user},
            [user.settings.email],
            user.settings.language
        )

    def post(self, *args, **kwargs):
        user = self.get_object()
        user.status = User.STATUS_ARCHIVED
        user.save()
        self.send_email_notification(user)
        if self.logout and self.request.user == user:
            logout(self.request)
        messages.success(self.request, _("Käyttäjätili %s suljettu.") % user)
        return HttpResponseRedirect(self.redirect_url)


class MessagesListView(generic.ListView):
    model = Message
    paginate_by = 5
    template_name = "account/messages/listing.html"

    user = None
    moderators = None

    FILTER_RECEIVED = "saapuneet"
    FILTER_SENT = "lahetetyt"
    FILTER_QUERY_STRING = "nayta"
    SORT_NEWEST = "uusin"
    SORT_OLDEST = "vanhin"
    SORT_QUERY_STRING = "jarjestys"

    filtering = FILTER_RECEIVED
    order_by = SORT_NEWEST

    def set_filtering(self):
        if self.request.GET.get(self.FILTER_QUERY_STRING):
            self.filtering = self.request.GET.get(self.FILTER_QUERY_STRING)

        # Non-moderators only see their own messages.
        if not self.user.is_moderator:
            if self.filtering == self.FILTER_RECEIVED:
                self.queryset = self.user.received_messages.all()
            elif self.filtering == self.FILTER_SENT:
                self.queryset = self.user.sent_messages.all()

        # Moderators see other moderators messages.
        else:
            if self.filtering == self.FILTER_RECEIVED:
                self.queryset = Message.objects.filter(
                    Q(to_moderator=True) | Q(receivers=self.user)
                )
            elif self.filtering == self.FILTER_SENT:
                self.queryset = Message.objects.filter(
                    Q(sender=self.user) | Q(from_moderator=True)
                )

            # Show one message only once.
            self.queryset = self.queryset.distinct()

    def set_ordering(self):
        if self.request.GET.get(self.SORT_QUERY_STRING):
            self.order_by = self.request.GET.get(self.SORT_QUERY_STRING)

        if self.order_by == self.SORT_NEWEST:
            self.queryset = self.queryset.order_by("-sent")
        elif self.order_by == self.SORT_OLDEST:
            self.queryset = self.queryset.order_by("sent")

    def exclude_deleted(self):
        self.queryset = self.queryset.exclude(deleted_by=self.user)

    def get_queryset(self):
        self.user = User.objects.get(pk=self.kwargs["user_id"])
        self.queryset = super(MessagesListView, self).get_queryset()
        self.set_filtering()
        self.set_ordering()
        self.exclude_deleted()
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(MessagesListView, self).get_context_data(**kwargs)
        context["object"] = self.user
        context["highlight_unread"] = self.filtering == self.FILTER_RECEIVED
        return context


class MessageDetailView(generic.DetailView):
    model = Message
    pk_url_kwarg = "message_id"
    template_name = "account/messages/detail.html"

    def get_context_data(self, **kwargs):
        context = super(MessageDetailView, self).get_context_data(**kwargs)
        context["message"] = self.get_object()
        context["object"] = User.objects.get(pk=self.kwargs["user_id"])
        context["message"].read_by.add(context["object"])
        return context


class CreateMessageView(generic.CreateView):
    model = Message
    template_name = "account/messages/create.html"
    form_class = MessageForm

    def get_form_kwargs(self):
        kwargs = super(CreateMessageView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super(CreateMessageView, self).get_initial()

        if "message_id" in self.kwargs:
            message_to_respond = Message.objects.get(pk=self.kwargs["message_id"])
            init_msg = "\n\n\n--- {0}: {1}, {2} ---\n{3}"
            init_msg = init_msg.format(
                _("Vastaus viestiin"),
                message_to_respond.subject,
                message_to_respond.sent,
                message_to_respond.message
            )
            initial.update({
                "receivers": [message_to_respond.sender],
                "subject": "Re: {}".format(message_to_respond.subject),
                "message": init_msg
            })

        receivers = self.request.GET.get("receivers")
        if receivers:
            initial.update({"receivers": [receivers]})

        return initial

    def get_success_url(self):
        messages.success(self.request, _("Viesti lähetetty."))
        return reverse("account:messages", args=[self.kwargs["user_id"]])

    def get_context_data(self, **kwargs):
        context = super(CreateMessageView, self).get_context_data(**kwargs)
        context["object"] = User.objects.get(pk=self.kwargs["user_id"])
        if "message_id" in self.kwargs:
            context["form_action"] = reverse(
                "account:respond_message",
                args=[self.kwargs["user_id"], self.kwargs["message_id"]]
            )
        else:
            context["form_action"] = reverse(
                "account:create_message",
                args=[self.kwargs["user_id"]]
            )
        return context

    def form_valid(self, form):
        message = form.save(commit=False)
        message.sender = User.objects.get(pk=self.kwargs["user_id"])
        if "message_id" in self.kwargs:
            message.reply_to = Message.objects.get(pk=self.kwargs["message_id"])
        if message.sender.is_moderator:
            message.from_moderator = True
        for receiver in form.cleaned_data["receivers"]:
            if receiver.is_moderator:
                message.to_moderator = True
                break
        message.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, _("Täytä kaikki pakolliset kentät."))
        return super(CreateMessageView, self).form_invalid(form)


class TransferIdeaMessageView(CreateMessageView):

    def get_idea(self):
        return Initiative.objects.get(pk=self.kwargs['initiative_id'])

    def get_initial(self):
        initial = super(TransferIdeaMessageView, self).get_initial()
        idea = self.get_idea()
        receivers = User.objects.filter(
            pk__in=idea.target_organization_admin_ids)
        initial.update({
            'message': '{0}\n{1}{2}'.format(
                _("Haluan viedä tämän idean eteenpäin."),
                settings.BASE_URL,
                idea.get_absolute_url()),
            'receivers': receivers,
            'subject': idea.title
        })
        return initial

    def get_context_data(self, **kwargs):
        context = super(TransferIdeaMessageView, self).get_context_data(**kwargs)
        context['form_action'] = self.request.path
        return context

    def get_success_url(self):
        messages.success(self.request, _("Viesti lähetetty yhteyshenkilölle."))
        return reverse('content:idea_detail', args=[self.kwargs['initiative_id']])

    def form_valid(self, form):
        # NOT IN USE FOR NOW
        #idea = self.get_idea()
        #if idea.status < Idea.STATUS_TRANSFERRED:
        #    idea.status = Idea.STATUS_TRANSFERRED
        #    idea.transferred = timezone.now()
        #    idea.save()

        return super(TransferIdeaMessageView, self).form_valid(form)


class DeleteMessageView(generic.DeleteView):
    model = Message
    pk_url_kwarg = "message_id"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = User.objects.get(pk=self.kwargs["user_id"])
        self.object.deleted_by.add(user)
        messages.success(self.request, _("Viesti poistettu postilaatikostasi."))
        return HttpResponseRedirect(reverse("account:messages", args=[user.pk]))


class NotificationOptionsEditView(UpdateView):
    model = User
    pk_url_kwarg = 'user_id'
    form_class = NotificationOptionsForm
    template_name = 'account/notification_options/options_edit.html'

    def get_success_url(self):
        return reverse('account:notification_options_detail', kwargs={
            'user_id': self.kwargs['user_id']})


class NotificationOptionsDetailView(DetailView):
    model = User
    pk_url_kwarg = 'user_id'
    form_class = NotificationOptionsForm
    template_name = 'account/notification_options/options_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['forms'] = OrderedDict()
        kwargs['forms']['notification_options'] = NotificationOptionsForm(
            instance=self.get_object())
        return kwargs

