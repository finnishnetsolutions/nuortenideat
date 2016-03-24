# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Municipality, Restructuring


class NaturalListFilter(admin.SimpleListFilter):
    title = _('Type')
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return (
            ('natural', _("Natural municipality")),
            ('magical', _("Reserved code")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'natural':
            return queryset.natural()
        if self.value() == 'magical':
            return queryset.magical()
        return queryset


class StatusListFilter(admin.SimpleListFilter):
    title = _('Status')
    parameter_name = 'activity_status'

    def lookups(self, request, model_admin):
        return (
            ('upcoming',    _("Upcoming")),
            ('active',      _("Active")),
            ('expiring',    _("Expiring")),
            ('expired',     _("Expired")),
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v in ('active', 'upcoming', 'expired', 'expiring'):
            return getattr(queryset, v)()
        return queryset


class OldRestructuringInline(admin.TabularInline):
    model = Restructuring
    fk_name = 'old_municipality'
    extra = 0

class NewRestructuringInline(admin.TabularInline):
    model = Restructuring
    fk_name = 'new_municipality'
    extra = 0


class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_fi', 'name_sv', 'beginning_date', 'expiring_date')
    list_filter = (NaturalListFilter, StatusListFilter, )
    inlines = (OldRestructuringInline, NewRestructuringInline, )
    readonly_fields = ('code', 'oid', 'name_fi', 'name_sv', 'created_date',
                       'last_modified_date')
    search_fields = ('code', 'name_fi', 'name_sv',)


admin.site.register(Municipality, MunicipalityAdmin)

