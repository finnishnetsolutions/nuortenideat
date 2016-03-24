# coding=utf-8

from __future__ import unicode_literals

from nuka import perms as nuka

from libs.permitter import perms


class IsOrganizationAdmin(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.organization = kwargs.pop('obj')
        super(IsOrganizationAdmin, self).__init__(**kwargs)

    def is_authorized(self):
        return bool(self.organization.admins.filter(pk=self.user.pk))


class OrganizationIsPublic(nuka.BasePermission):
    def __init__(self, **kwargs):
        self.organization = kwargs['obj']
        super(OrganizationIsPublic, self).__init__(**kwargs)

    def is_authorized(self):
        return self.organization.is_active is True and self.organization.type is not \
                                                       self.organization.TYPE_UNKNOWN


CanViewOrganization = perms.Or(
    OrganizationIsPublic,
    perms.And(
        nuka.IsAuthenticated,
        perms.Or(IsOrganizationAdmin, nuka.IsModerator)
    )
)


CanEditOrganization = perms.And(
    nuka.IsAuthenticated,
    perms.Or(IsOrganizationAdmin, nuka.IsModerator)
)
