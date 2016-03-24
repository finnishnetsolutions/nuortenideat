# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.contrib.comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from nocaptcha_recaptcha import NoReCaptchaField
from libs.attachtor.forms.forms import RedactorAttachtorFormMixIn
from nkcomments.models import CustomComment

from nuka.forms.fields import SaferRedactorField


class BaseCustomCommentForm(CommentForm):
    honeypot = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
        label=_('If you enter anything in this field your comment '
                'will be treated as spam')
    )

    def get_comment_create_data(self):
        return dict(
            content_type=ContentType.objects.get_for_model(self.target_object),
            object_pk=force_text(self.target_object._get_pk_val()),
            user_name=self.cleaned_data["name"],
            comment=self.cleaned_data["comment"],
            submit_date=timezone.now(),
            site_id=settings.SITE_ID,
            is_public=True,
            is_removed=False,
        )

    def get_comment_model(self):
        return CustomComment


class CustomCommentFormAnon(BaseCustomCommentForm):
    captcha = NoReCaptchaField(
        label=_('Tarkistuskoodi'),
        error_messages={'invalid': _('Virheellinen tarkistuskoodi.')},
    )


class CustomCommentForm(RedactorAttachtorFormMixIn, BaseCustomCommentForm):
    name = forms.CharField(widget=forms.HiddenInput, required=False)
    comment = SaferRedactorField(allow_file_upload=True, allow_image_upload=True,
                                 label=_('Kommentti'))


class CommentEditForm(RedactorAttachtorFormMixIn, forms.ModelForm):
    comment = SaferRedactorField(allow_file_upload=True, allow_image_upload=True,
                                 label=_('Kommentti'))

    class Meta:
        model = CustomComment
        fields = ('comment', )


class AnonCommentEditForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea, label=_("Kommentti"))

    class Meta:
        model = CustomComment
        fields = ('comment', )


CustomCommentFormAnon.base_fields.pop('email')
CustomCommentFormAnon.base_fields.pop('url')
CustomCommentForm.base_fields.pop('email')
CustomCommentForm.base_fields.pop('url')



