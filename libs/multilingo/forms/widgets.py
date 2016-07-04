# coding=utf-8

from __future__ import unicode_literals

import json

from django.forms.widgets import MultiWidget, TextInput, Textarea
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import get_language


class SingleLanguageWidgetMixIn(object):
    def __init__(self, attrs=None, **kwargs):
        if attrs is None:
            attrs = {"class": "multilingo-input"}
        super(SingleLanguageWidgetMixIn, self).__init__(attrs=attrs, **kwargs)

    def render(self, name, value, attrs=None):
        attrs = (attrs or {}).copy()
        final_attrs = self.build_attrs(attrs)
        label = final_attrs.pop('data-language-label', None) or \
            final_attrs.get('data-language-label', None)
        html = ''
        if label:
            html += mark_safe('<div class="language-label">%s</div>' % escape(label))
        html += super(SingleLanguageWidgetMixIn, self).render(name, value, attrs=attrs)
        return html


class SingleLanguageTextInput(SingleLanguageWidgetMixIn, TextInput):
    pass


class SingleLanguageTextarea(SingleLanguageWidgetMixIn, Textarea):
    pass


class MultiLingualWidget(MultiWidget):
    widget_class = SingleLanguageTextInput
    init_js = """
    <script type="text/javascript">
        $(function () {
            var wrap = $('#%(id)s').closest('.multilingo-wrap');
            if (!wrap.length) {
                wrap = $('#%(id)s').closest('form');
            }
            if (wrap.data('multilingo')) {
                wrap.multilingo('refresh');
            }
            else {
                wrap.multilingo(%(options)s);
            }
        });
    </script>
    """

    def __init__(self, **kwargs):
        self.languages = kwargs.pop('languages', ())
        if 'widget_class' in kwargs:
            self.widget_class = kwargs.pop('widget_class')
        if not 'widgets' in kwargs:
            kwargs['widgets'] = [
                self.widget_class(attrs={'data-language-label': lang[1],
                                         'data-language-code': lang[0]})
                for lang in self.languages
            ]
        super(MultiLingualWidget, self).__init__(**kwargs)

    def render(self, name, value, attrs=None):
        if self.is_localized:
            for widget in self.widgets:
                widget.is_localized = self.is_localized
        # value is a list of values, each corresponding to a widget
        # in self.widgets.
        if not isinstance(value, list):
            value = self.decompress(value)
        output = []
        final_attrs = self.build_attrs(attrs)
        final_attrs.pop('required', None)  # TODO: how to properly control this?
        id_ = final_attrs.get('id', None)
        for i, widget in enumerate(self.widgets):
            if isinstance(value, dict):
                widget_value = value.get(self._lang_code(i), None)
            elif isinstance(value, list) and len(value) > i:
                widget_value = value[i]
            else:
                widget_value = None
            if id_:
                final_attrs = dict(final_attrs,
                                   id='%s-%s' % (id_, self._lang_code(i)))
            html = '<div class="multilingo-language-version" ' \
                   'data-language-code="%s">' % self._lang_code(i)
            html += widget.render(name + '-%s' % self._lang_code(i), widget_value,
                                  final_attrs)
            html += '</div>'
            output.append(html)
        html = mark_safe(
            '<div id="%s" class="multilingo-field">' % id_ +
            self.format_output(output) +
            '</div>' +
            self.init_js % {
                'id': id_,
                'options': json.dumps(self.get_options())
            }
        )
        return html

    def get_options(self):
        return {
            'languages': map(lambda l: {'code': l[0], 'label': l[1]}, self.languages),
            'activeLanguage': get_language()
        }

    def _lang_code(self, i):
        return self.languages[i][0]

    def value_from_datadict(self, data, files, name):
        return [widget.value_from_datadict(data, files,
                                           name + '-%s' % self._lang_code(i))
                for i, widget in enumerate(self.widgets)]

    def decompress(self, value):
        if not value:
            return dict()
        return value
