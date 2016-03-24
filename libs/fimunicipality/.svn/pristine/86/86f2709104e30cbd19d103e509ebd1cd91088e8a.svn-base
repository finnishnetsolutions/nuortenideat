# coding=utf-8

from __future__ import unicode_literals

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone, translation
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


class MunicipalityQuerySet(models.QuerySet):
    def active(self):
        today = timezone.now().date()
        return self.filter(beginning_date__lte=today,
                           expiring_date__gte=today)

    def expired(self):
        return self.filter(expiring_date__lt=timezone.now().date())

    def expiring(self):
        today = timezone.now().date()
        return self.filter(expiring_date__gt=today,
                           expiring_date__lt=today+timedelta(days=365*5))

    def upcoming(self):
        return self.filter(beginning_date__gt=timezone.now().date())

    def natural(self):
        return self.exclude(code__in=self.model.MAGIC_CODES)

    def magical(self):
        return self.filter(code__in=self.model.MAGIC_CODES)


@python_2_unicode_compatible
class Municipality(models.Model):
    CODE_NO_HOME_MUNICIPALITY_IN_FINLAND = '198'
    CODE_UNKNOWN = '199'
    CODE_ABROAD = '200'

    MAGIC_CODES = (CODE_NO_HOME_MUNICIPALITY_IN_FINLAND, CODE_UNKNOWN, CODE_ABROAD)

    # data from CodeService
    code = models.CharField(max_length=3)
    oid = models.CharField(max_length=32, unique=True, null=True, blank=True)
    name_fi = models.CharField(max_length=50, db_index=True)
    name_sv = models.CharField(max_length=50, db_index=True)

    beginning_date = models.DateField()
    expiring_date = models.DateField()
    created_date = models.DateField()
    last_modified_date = models.DateField()

    # automatic timestamps
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = MunicipalityQuerySet.as_manager()

    def is_active(self):
        return self.beginning_date <= timezone.now().date() <= self.expiring_date

    def clean(self):
        val = super(Municipality, self).clean()
        if self.oid is None and self.code not in self.MAGIC_CODES:
            raise ValidationError("oid cannot be None unless code is magical")
        if self.code in self.MAGIC_CODES and self.oid is not None:
            raise ValidationError("oid must be None if code is magical")
        return val

    @property
    def name(self):
        lang = translation.get_language()
        if lang in ('sv', 'fi'):
            return getattr(self, '_'.join(['name', lang]))
        return self.name_fi

    @property
    def long_name(self):
        return ' '.join([self.code, self.name])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("Municipality")
        verbose_name_plural = _("Municipalities")
        index_together = (('beginning_date', 'expiring_date',), )


class Restructuring(models.Model):
    old_municipality = models.ForeignKey(Municipality,
                                         related_name='new_municipalities',
                                         verbose_name=_("New municipalities"))
    new_municipality = models.ForeignKey(Municipality,
                                         related_name='old_municipalities',
                                         verbose_name=_("Former municipalities"))
    old_code = models.CharField(max_length=3)
    new_code = models.CharField(max_length=3)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('old_municipality', 'new_municipality',), )
