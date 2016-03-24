# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth import admin as auth
from django.utils.translation import ugettext_lazy as _

from models import User, UserSettings


class UserAdmin(auth.UserAdmin):
    list_display = ('username', 'status', 'is_staff', 'joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'status', 'groups')
    search_fields = ('username', 'settings__first_name', 'settings__last_name',
                     'settings__email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        #(_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('status', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions',)}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )



admin.site.register(User, UserAdmin)
