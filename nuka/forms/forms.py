# coding=utf-8

from __future__ import unicode_literals


class HiddenLabelMixIn(object):
    def __init__(self, *args, **kwargs):
        super(HiddenLabelMixIn, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label:
                field.widget.attrs["aria-label"] = field.label
            field.label = ""