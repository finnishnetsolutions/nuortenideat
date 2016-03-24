# coding=utf-8

from __future__ import unicode_literals

from .forms import ModReasoningFormMixIn


def get_moderated_form_class(non_moderated_form_class, moderator):
    return type(
        str('Moderator' + non_moderated_form_class.__name__),
        (ModReasoningFormMixIn, non_moderated_form_class),
        {'_moderator': moderator}
    )
