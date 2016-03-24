# coding=utf-8

from __future__ import unicode_literals

import json
from uuid import uuid4

from django import forms
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from nuka.utils import send_email_to_multiple_receivers
from account.models import User

from .models import ContentFlag, ModerationReason


class FlagContentForm(forms.ModelForm):
    class Meta:
        model = ContentFlag
        fields = ('reason', )


class ModReasoningFormMixIn(object):
    def __init__(self, *args, **kwargs):
        super(ModReasoningFormMixIn, self).__init__(*args, **kwargs)
        self.fields['_moderation_reason'] = ModReasoningField(max_length=250)

    @transaction.atomic
    def save(self, *args, **kwargs):
        instance = super(ModReasoningFormMixIn, self).save(*args, **kwargs)
        reason = ModerationReason(content_object=instance, moderator=self._moderator,
                                  reason=self.cleaned_data['_moderation_reason'])
        reason.save(force_insert=True)

        send_email_to_multiple_receivers(
            _("Sisältöä moderoitu."),
            'nkmoderation/email/content_modified_message.txt',
            {'link': instance.get_absolute_url(), 'reason': reason.reason},
            self.get_notify_receivers(instance)
        )
        return instance

    def get_notify_receivers(self, instance):
        return User.objects.filter(pk__in=instance.owner_ids)


class ModReasoningWidget(forms.HiddenInput):
    template_name = 'nkmoderation/moderation_reasoning.html'

    init_js = """
    <script>
        $(function () {
            var wrap = $('#%(id)s').parents('.modreasoning-wrap').first();
            if (!wrap.length) {
                wrap = $('#%(id)s').parents('form').first();
            }
            if (!wrap.data('modreasoning')) {
                wrap.modreasoning(%(options)s);
            } else {
                console.log('wrap already reasoning');
            }
        });
    </script>
    """

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        # force unique id, since there may be multiple edit forms on the same page
        id_ = '%s_%s' % (final_attrs.get('id'), uuid4().hex[:6])
        attrs['id'] = id_
        html = super(ModReasoningWidget, self).render(name, value, attrs)
        form_id = '%s-reasoning-form' % id_
        reason_form_html= render_to_string(self.template_name, {
            'id': form_id,
            'initial_reason': '',
        })
        opts = {'reasonFieldSelector': '#%s' % id_,
                'triggerEvent': 'beforeAjaxySubmit',
                'reasonFormHtml': reason_form_html, }
        html += mark_safe(self.init_js % {
            'id': id_,
            'options': json.dumps(opts),
        })
        return html


class ModReasoningField(forms.CharField):
    widget = ModReasoningWidget
