# coding=utf-8

from __future__ import unicode_literals

import factory

from django.contrib.contenttypes.models import ContentType

from content.models import Idea
from .models import CustomComment


class CustomCommentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CustomComment

    site_id = 1
    user_name = factory.Sequence(lambda n: 'user_{0}'.format(n))
    email = factory.Sequence(lambda n: 'tester_{0}@test.dev'.format(n))
    comment = factory.Sequence(lambda n: 'Awesome! I thumbed up this idea for {0} times.'.format(n))
    content_type = factory.LazyAttribute(lambda o:
                                         ContentType.objects.get_for_model(Idea))



