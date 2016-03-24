# coding=utf-8

from __future__ import unicode_literals


class FieldReAttrMixIn(object):
    overrides = (
        ('labels', 'label'),
        ('widgets', 'widget'),
    )

    def __init__(self, *args, **kwargs):
        super(FieldReAttrMixIn, self).__init__(*args, **kwargs)
        for container_postfix, attr in self.overrides:
            for k, v in self._get_attr_container(container_postfix):
                if k == '*':
                    for f in self.fields.values():
                        setattr(f, attr, v)
                elif k in self.fields:
                    setattr(self.fields[k], attr, v)

    def _get_attr_container(self, postfix):
        return getattr(self, 'field_{}'.format(postfix), ())


class LabellessFieldsMixIn(FieldReAttrMixIn):
    """Sets an empty label for all fields in a Form."""
    field_labels = (
        ('*', ''),
    )


class FieldPlaceholdersMixIn(object):
    """Injects placeholder-attributes to Form field widgets' attrs."""

    placeholders = (
        #('field_name', _("Placeholder text")),
    )

    def __init__(self, *args, **kwargs):
        super(FieldPlaceholdersMixIn, self).__init__(*args, **kwargs)
        for f, placeholder in self.placeholders:
            if f in self.fields:
                self.fields[f].widget.attrs['placeholder'] = placeholder
