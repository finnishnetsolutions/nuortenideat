# coding=utf-8

from __future__ import unicode_literals


import factory
from tagging.factories import TagFactory

from tagging.models import Tag
from account.factories import UserFactory
from organization.factories import OrganizationFactory

from .models import Idea, AdditionalDetail, Question


class BaseInitiativeFactory(factory.DjangoModelFactory):

    creator = factory.SubFactory(UserFactory)

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for owner in extracted:
                self.owners.add(owner)
        else:
            self.owners.add(self.creator)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            self.tags.add(TagFactory())

    @factory.post_generation
    def target_organizations(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for org in extracted:
                self.target_organizations.add(org)
        else:
            self.target_organizations.add(OrganizationFactory())


class IdeaFactory(BaseInitiativeFactory):
    FACTORY_FOR = Idea

    visibility = Idea.VISIBILITY_PUBLIC
    status = Idea.STATUS_PUBLISHED
    title = factory.Sequence(lambda n: 'Bright Idea {0}'.format(n))
    description = "Let's do, like, some stuff, that is like cool and stuff."


class AdditionalDetailFactory(factory.DjangoModelFactory):
    FACTORY_FOR = AdditionalDetail

    idea = factory.SubFactory(IdeaFactory)
    detail = factory.Sequence(lambda n: '{0} things that I forgot'.format(n))


class QuestionFactory(BaseInitiativeFactory):
    FACTORY_FOR = Question

    title = factory.Sequence(lambda n: 'I want to be a tester no {0}'.format(n))
    description = "Can I practise some more testing?."