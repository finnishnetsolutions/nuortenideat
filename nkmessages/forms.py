# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from nkmessages.models import Message, Feedback


class FeedbackForm(forms.ModelForm):
    message = forms.CharField(label=_('Viesti'), widget=forms.Textarea)

    def __init__(self, user=None, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        if user:
            del self.fields["name"]
            del self.fields["email"]

    class Meta:
        model = Feedback
        fields = ("name", "email", "subject", "message")