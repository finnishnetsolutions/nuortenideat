# coding=utf-8

from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.edit import CreateView

from .forms import FeedbackForm
from .models import Feedback


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
        messages.success(self.request, _("Kiitos palautteesta! Palaute on lähetetty."))
        return HttpResponseRedirect(reverse("frontpage"))