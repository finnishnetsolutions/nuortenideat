# coding=utf-8

from __future__ import unicode_literals

import factory

from .models import ParticipatingMunicipality, KuaInitiative, KuaInitiativeStatus


class ParticipatingMunicipalityFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ParticipatingMunicipality

    municipality = factory.SubFactory('organization.factories.MunicipalityFactory')


class KuaInitiativeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = KuaInitiative

    kua_id = factory.Sequence(lambda n: n)
    idea = factory.SubFactory('content.factories.IdeaFactory')
    created_by = factory.SubFactory('account.factories.UserFactory')


class KuaInitiativeStatusFactory(factory.DjangoModelFactory):
    FACTORY_FOR = KuaInitiativeStatus

    kua_initiative = factory.SubFactory(KuaInitiativeFactory)
