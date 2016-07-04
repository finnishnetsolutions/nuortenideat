# coding=utf-8

from __future__ import unicode_literals


from libs.bs3extras.renderers import AccessibleWrapIdFieldRenderer, \
    InstructionedFieldRendererMixin
from libs.formidable.forms.renderers import InlineFormFieldRendererMixIn


class NukaFieldRenderer(InstructionedFieldRendererMixin,
                             InlineFormFieldRendererMixIn,
                             AccessibleWrapIdFieldRenderer):
    pass
