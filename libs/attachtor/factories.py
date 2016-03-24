# coding=utf-8

from __future__ import unicode_literals

from uuid import uuid4

import factory

from .models import UploadGroup, Upload


class UploadGroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UploadGroup

    id = factory.LazyAttribute(uuid4().hex)


class UploadFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Upload

    group = factory.SubFactory(UploadGroupFactory)
