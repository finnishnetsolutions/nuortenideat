# coding=utf-8

from __future__ import unicode_literals

import factory

from .models import Tag


class TagFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Tag

    name = factory.Sequence(lambda n: 'Test Tag #{0:d}'.format(n))

