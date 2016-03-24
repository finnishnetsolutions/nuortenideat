# coding=utf-8

from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social.exceptions import AuthCanceled


class CustomSocialExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) is AuthCanceled:
            messages.error(request, _("Facebookin yhdistäminen peruutettiin."))
            strategy = getattr(request, 'social_strategy', None)
            action = strategy.session_get("action")
            if action == "login":
                return redirect("account:login")
            elif action == "signup":
                return redirect("account:signup_choices")
            elif action == "associate":
                return redirect("account:settings", user_id=request.user.pk)