# coding=utf-8

from __future__ import unicode_literals


class CleanedDataWithForm(dict):
    """
    A HACK to allow InlineFormSetFieldMixin.clean() to return the cleaned Form instances
    along with their cleaned data dict. Avoids having to clean the inline forms again at
    InlineModelFormSetMixIn.save().
    """
    def __init__(self, *args, **kwargs):
        self.cleaned_form = kwargs.pop('form')
        super(CleanedDataWithForm, self).__init__(*args, **kwargs)


class DataListWithDeletedPKs(list):
    """
    A HACK to supply deleted object primary keys with the list of data dicts to be
    validated from the InlineFormSetWidget to the Field for validation..
    """
    def __init__(self, *args, **kwargs):
        self.deleted_pks = kwargs.pop('deleted_pks', [])
        super(DataListWithDeletedPKs, self).__init__(*args, **kwargs)
