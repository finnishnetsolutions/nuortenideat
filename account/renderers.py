# coding=utf-8
from __future__ import unicode_literals

from bootstrap3.renderers import FieldRenderer
from django.forms.widgets import HiddenInput
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext as _


class NotificationOptionsFieldPreviewRenderer(FieldRenderer):

    def get_label(self):
        return self.field.field.choices[0][1]

    def render(self):
        html = self.field.as_widget(widget=HiddenInput(),
                                    attrs=self.widget.attrs)
        v = self.field.value()
        notify = self.field.field.choices[0][0]
        if notify in v:
            v.remove(notify)

        choices_dict = dict(self.field.field.choices[1:])
        labels = ", ".join([force_text(choices_dict[value]) for value in v])
        html += '<p>{0}</p>'.format(escape(labels or _("Ei")))
        html = html or ''
        html = self.append_to_field(html)
        html = self.add_label(html)
        html = self.wrap_label_and_field(html)
        return html
