# coding=utf-8

from __future__ import unicode_literals

import json

from django import forms
from django.forms.widgets import SelectMultiple, Select
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext

from libs.attachtor.forms.widgets import RedactorAttachtorWidget
from libs.multilingo.forms import widgets as multilingo


class Select2Multiple(SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        output = super(Select2Multiple, self).render(name, value, attrs, choices)
        return mark_safe(output + '<script>$("#%s").select2();</script>' % attrs['id'])


class Select2(Select):
    def render(self, name, value, attrs=None, choices=()):
        output = super(Select2, self).render(name, value, attrs, choices)
        return mark_safe(output + '<script>$("#%s").select2();</script>' % attrs['id'])


class ButtonSelectMixIn(object):
    def render(self, name, value, attrs=None, choices=()):
        if attrs is not None:
            opts = attrs.pop('buttonselect', {})
        else:
            opts = {}
        output = super(ButtonSelectMixIn, self).render(name, value, attrs, choices)
        return mark_safe(output + '<script>$("#%s").buttonSelect(%s);</script>' %
                         (attrs['id'], json.dumps(opts)))


class ButtonSelect(ButtonSelectMixIn, forms.Select):
    pass


class AutoSubmitButtonSelect(forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        if attrs is not None:
            opts = attrs.pop('buttonselect', {})
        else:
            opts = {}
        opts['changeEvent'] = 'change'
        output = super(AutoSubmitButtonSelect, self).render(name, value, attrs, choices)
        return mark_safe(output + """
            <script>
                $("#%s").buttonSelect(%s).on('change', function() {
                    $(this).parents('form').first().submit();
                });
            </script>
            """ % (attrs['id'], json.dumps(opts)))


class SingleLanguageRedactorAttachtorWidget(multilingo.SingleLanguageWidgetMixIn,
                                            RedactorAttachtorWidget):
    pass


class MultiLingualWidget(multilingo.MultiLingualWidget):
    def get_options(self):
        opts = super(MultiLingualWidget, self).get_options()
        opts.update({
            'langChoiceText': ugettext("Kieliversiot")
        })
        return opts
