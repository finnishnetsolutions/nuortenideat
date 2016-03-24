from django.contrib import admin

from django.contrib import admin

from .models import ParticipatingMunicipality, KuaInitiative, KuaInitiativeStatus


class ParticipatingMunicipalityAdmin(admin.ModelAdmin):
    list_display = ('municipality', 'created', )
    search_fields = ('municipality__code',
                     'municipality__name_fi',
                     'municipality__name_sv', )


class KuaInitiativeStatusAdmin(admin.ModelAdmin):
    list_display = ('kua_initiative', 'status', 'created',)

admin.site.register(ParticipatingMunicipality, ParticipatingMunicipalityAdmin)
admin.site.register(KuaInitiative)
admin.site.register(KuaInitiativeStatus, KuaInitiativeStatusAdmin)
