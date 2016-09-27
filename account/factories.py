# coding=utf-8

from __future__ import unicode_literals
from datetime import timedelta
from django.utils import timezone

import factory

from .models import User, UserSettings


DEFAULT_PASSWORD = 'letsgo123!'


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    status = User.STATUS_ACTIVE

    username = factory.Sequence(lambda n: 'user_{0}'.format(n))
    password = factory.PostGenerationMethodCall('set_password', DEFAULT_PASSWORD)
    settings = factory.RelatedFactory('account.factories.UserSettingsFactory', "user")
    last_login = factory.LazyAttribute(lambda a: timezone.now())

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)

class UserSettingsFactory(factory.DjangoModelFactory):
    FACTORY_FOR = UserSettings

    user = factory.SubFactory(UserFactory, settings=None)
    first_name = factory.Sequence(lambda n: 'Jack the {0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Black{0}'.format(n))
    email = factory.Sequence(lambda n: 'tester_{0}@test.dev'.format(n))
    birth_date = timezone.now().date() - timedelta(days=13*365)
    municipality = factory.SubFactory('organization.factories.MunicipalityFactory')
