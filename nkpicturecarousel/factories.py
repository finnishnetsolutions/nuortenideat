# coding=utf-8

from __future__ import unicode_literals

import factory

from .models import PictureCarouselSet, PictureCarouselImage


# UNTESTED AND CURRENTLY NOT USED ANYWHERE!

class PictureCarouselSetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PictureCarouselSet

    name = factory.Sequence(lambda n: 'Test carousel set #{}'.format(n))


class PictureCarouselImageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PictureCarouselImage

    carousel_set = factory.SubFactory(PictureCarouselSetFactory)
    alt_text = factory.Sequence(lambda n: 'Carousel picture #{}'.format(n))