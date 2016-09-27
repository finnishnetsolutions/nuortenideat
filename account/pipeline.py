# coding=utf-8

from __future__ import unicode_literals
from datetime import date

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.template.defaultfilters import date

from social.pipeline.partial import partial
from nuka.settings import LANGUAGES

""" AUTH FUNCTIONS """

BACKEND_KEY_FB = 'facebook'
BACKEND_KEY_GOOGLE = 'google-oauth2'

BACKEND_NAMES = {
    BACKEND_KEY_FB: 'Facebook',
    BACKEND_KEY_GOOGLE: 'Google',
}


def get_backend_readable_name(name):
    print name, 'NIMIMIMIIMIMI'
    return BACKEND_NAMES.get(name, '')


def get_language(lang):
    language_codes = [x for x, y in LANGUAGES]
    if lang in language_codes:
        return lang
    return ''


def get_response_values(name, response):
    mapped = {'id': response.get('id'), 'language': ''}

    if name == BACKEND_KEY_FB:
        pic_url = "http://graph.facebook.com/{}/picture?type=large".format(
            mapped['id'])
        mapped.update({
            'picture': pic_url,
            'first_name': response.get('first_name'),
            'last_name': response.get('last_name'),
            'email': response.get('email'),
        })
    elif name == BACKEND_KEY_GOOGLE:
        img = response.get('image', {})
        pic_url = img.get('url', '') if not img.get('isDefault') else ''
        if pic_url:
            pic_url = pic_url.replace('sz=50', 'sz=200')
        name = response.get('name', {})
        emails = response.get('emails', [])
        email = ''
        if len(emails):
            email_dict = emails[0]
            if isinstance(email_dict, dict):
                email = email_dict.get('value', '')

        mapped.update({
            'picture': pic_url,
            'first_name': name.get('givenName', ''),
            'last_name': name.get('familyName', ''),
            'email': email,
            'language': get_language(response.get('language', '')),
        })

    return mapped


def performed_action(strategy, *args, **kwargs):
    return {"action": strategy.session_get("action")}


def social_user(strategy, backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            messages.error(strategy.request, _("{}-tili on jo käytössä.".format(
                get_backend_readable_name(provider)
            )))
            return redirect("account:settings", user_id=user.pk)
        elif not user:
            user = social.user

    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}


def prevent_duplicate_signup(strategy, user, social, action, *args, **kwargs):
    if user and social and action == "signup":
        messages.info(strategy.request, _("{}-tili on jo käytössä.".format(
            get_backend_readable_name(kwargs['backend'].name)
        )))
        return redirect("account:signup_choices")


@partial
def logged_user(strategy, is_new, action, response, *args, **kwargs):
    if is_new:
        # If there is user logged in, return it.
        user = strategy.request.user
        if user.is_authenticated():
            return {"user": user}

        # If user is not logged in, send to login or signup page.
        else:
            if action == "login":
                messages.info(
                    strategy.request,
                    _("{0}-tiliä ei ole yhdistetty. Rekisteröidy {0}-tunnuksillasi tai "
                      "yhdistä se jo olemassaolevaan Nuortenideat.fi-tunnukseen Oma sivun"
                      " asetuksista.".format(
                            get_backend_readable_name(kwargs['backend'].name)))
                )

                return redirect("account:login")
            elif action == "signup":
                strategy.request.session['social'] = get_response_values(
                    kwargs['backend'].name, response)
                print strategy.request.session['social']
                #strategy.request.session["fb_id"] = response.get("id")
                #strategy.request.session["fb_email"] = response.get("email")
                #strategy.request.session["fb_first_name"] = response.get("first_name")
                #strategy.request.session["fb_last_name"] = response.get("last_name")
                return redirect("account:signup_{}".format(kwargs['backend'].name))


def set_messages(strategy, is_new, new_association, user, social, backend, *args, **kwargs):
    if not user and not social:
        return
    elif not is_new and new_association:
        messages.success(
            strategy.request,
            _("{0}-yhteys luotu. Voit jatkossa kirjautua palveluun {0}-tunnuksillasi.".
                format(get_backend_readable_name(backend.name)))
        )
    elif is_new:
        return
    else:
        messages.success(strategy.request, _("Tervetuloa! Käytit palvelua viimeksi %s.") %
                         date(user.last_login, 'DATETIME_FORMAT'))


""" DISCONNECT FUNCTIONS """


def set_disconnect_messages(strategy, user, backend, *args, **kwargs):
    messages.success(strategy.request, _("{}-yhteys poistettu.".format(
        get_backend_readable_name(backend.name)
    )))
