# coding=utf-8

from __future__ import unicode_literals

from django.conf import settings
from django.template.defaultfilters import date
from django.utils.translation import ugettext
from import_export import resources, fields
from content.models import AdditionalDetail

from .models import Initiative


class InitiativeResource(resources.ModelResource):

    title = fields.Field(column_name=ugettext("Otsikko"))
    owners = fields.Field(column_name=ugettext("Omistajat"))
    tags = fields.Field(column_name=ugettext("Aiheet"))
    link = fields.Field(column_name=ugettext("Linkki"))
    votes_up = fields.Field(column_name=ugettext("Kannattaa"))
    votes_down = fields.Field(column_name=ugettext("Vastustaa"))
    status = fields.Field(column_name=ugettext("Tila"))
    transferred = fields.Field(column_name=ugettext("Viety eteenpäin"))
    target_organizations = fields.Field(column_name=ugettext("Kohdeorganisaatiot"))

    def dehydrate_title(self, initiative):
        return initiative.title

    def dehydrate_tags(self, initiative):
        return " ".join(["#%s" % t.name for t in initiative.tags.all()])

    def dehydrate_link(self, initiative):
        return settings.BASE_URL + initiative.get_absolute_url()

    def dehydrate_owners(self, initiative):
        if not initiative.is_idea():
            if not initiative.owners.all():
                if initiative.user_email:
                    return "{} ({})".format(initiative.user_name, initiative.user_email)
                return initiative.user_name

        if initiative.initiator_organization:
            return initiative.initiator_organization
        else:
            return " ".join([o.get_short_name() for o in initiative.owners.all()])

    def dehydrate_target_organizations(self, initiative):
        return " ".join(["%s" % o.name for o in initiative.target_organizations.all()])

    def dehydrate_votes_up(self, initiative):
        if not initiative.is_idea():
            return ''
        return initiative.votes.up().count()

    def dehydrate_votes_down(self, initiative):
        if not initiative.is_idea():
            return ''
        return initiative.votes.down().count()

    def dehydrate_status(self, initiative):
        if initiative.is_idea():
            return initiative.status_or_visibility()
        return initiative.get_visibility_display()

    def dehydrate_transferred(self, initiative):
        if initiative.is_idea() and initiative.transferred:
            transfer_date = date(initiative.transferred, 'SHORT_DATE_FORMAT')
            messages = []
            for d in initiative.details.all():
                if d.type == AdditionalDetail.TYPE_TRANSFERRED:
                    messages.append("%s" % d.detail)
            if len(messages):
                return "{}: {}".format(transfer_date, " --- ".join(messages))
            return transfer_date
        return ''

    class Meta:
        model = Initiative
        fields = ('link', 'title', 'tags', 'owners', 'target_organizations',
                  'votes_up', 'votes_down', 'status', 'transferred')
        export_order = ('title', 'owners', 'target_organizations', 'tags', 'votes_up',
                        'votes_down', 'status', 'link', )
