# coding=utf-8

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView
from account.models import User, GROUP_NAME_MODERATORS, GROUP_NAME_ADMINS

from .forms import FeedbackForm
from .models import Feedback
from nuka.utils import send_email_to_multiple_receivers


class FeedbackView(CreateView):
    model = Feedback
    template_name = "nkmessages/feedback_form.html"
    form_class = FeedbackForm

    def get_form_kwargs(self):
        kwargs = super(FeedbackView, self).get_form_kwargs()
        if self.request.user.is_authenticated():
            kwargs["user"] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        feedback = form.save(commit=False)
        feedback.to_moderator = True
        if self.request.user.is_authenticated():
            feedback.sender = self.request.user
        feedback.save()
        form.save_m2m()

        moderators = User.objects.filter(
            groups__name__in=(GROUP_NAME_MODERATORS, GROUP_NAME_ADMINS))

        send_email_to_multiple_receivers(
            title=_("Saapunut palaute"),
            msg_template='nkmessages/email/new_feedback.txt',
            users=moderators
        )

        messages.success(self.request, _("Kiitos palautteesta! Palaute on lähetetty."))
        return HttpResponseRedirect(reverse("frontpage"))