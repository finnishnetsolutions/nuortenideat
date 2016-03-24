# coding=utf-8

from __future__ import unicode_literals
from datetime import date

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.template.defaultfilters import date

from social.pipeline.partial import partial


""" AUTH FUNCTIONS """


def performed_action(strategy, *args, **kwargs):
    return {"action": strategy.session_get("action")}


def social_user(strategy, backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            messages.error(strategy.request, _("Facebook-tili on jo käytössä."))
            return redirect("account:settings", user_id=user.pk)
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}


def prevent_duplicate_signup(strategy, user, social, action, *args, **kwargs):
    if user and social and action == "signup":
        messages.info(strategy.request, _("Facebook-tili on jo käytössä."))
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
                    _("Facebook-tiliä ei ole yhdistetty. Rekisteröidy "
                      "Facebook-tunnuksillasi tai yhdistä se jo olemassaolevaan "
                      "Nuortenideat.fi-tunnukseen oma sivun asetuksista.")
                )
                return redirect("account:login")
            elif action == "signup":
                strategy.request.session["fb_id"] = response.get("id")
                strategy.request.session["fb_email"] = response.get("email")
                strategy.request.session["fb_first_name"] = response.get("first_name")
                strategy.request.session["fb_last_name"] = response.get("last_name")
                return redirect("account:signup_facebook")


def set_messages(strategy, is_new, new_association, user, social, *args, **kwargs):
    if not user and not social:
        return
    elif not is_new and new_association:
        messages.success(strategy.request, _("Facebook-yhteys luotu. Voit jatkossa "
                                             "kirjautua palveluun "
                                             "facebook-tunnuksillasi."))
    elif is_new:
        return
    else:
        messages.success(strategy.request, _("Tervetuloa! Käytit palvelua viimeksi %s.") %
                         date(user.last_login, 'DATETIME_FORMAT'))


""" DISCONNECT FUNCTIONS """


def set_disconnect_messages(strategy, user, *args, **kwargs):
    messages.success(strategy.request, _("Facebook-yhteys poistettu."))
