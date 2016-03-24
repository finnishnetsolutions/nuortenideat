# coding=utf-8

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from account.factories import UserFactory, DEFAULT_PASSWORD, UserSettingsFactory
from nuka.test.testcases import TestCase
from account.models import User, GROUP_NAME_ADMINS, GROUP_NAME_MODERATORS
from django.contrib.auth.models import Group
from organization.factories import MunicipalityFactory
from organization.models import Organization

from .views import QS_ORDER_BY, QS_SEARCH


class UsersListUnauthorizedAccessTest(TestCase):

    def test_anonymous_redirect(self):
        resp = self.client.get("/fi/hallinta/kayttajat/", follow=True)
        self.assertContains(resp, 'Kirjaudu sisään tai rekisteröidy ' +
                            'käyttääksesi toimintoa.', status_code=200)

    def test_unauthorized_redirect(self):
        user = UserFactory()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/", follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Toiminto vaatii moderaattorin oikeudet')
        self.assertContains(resp, 'Kirjaudu sisään')


class UsersListAuthorizedAccessTest(TestCase):

    def setUp(self):
        self.group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        self.group_moderator = Group.objects.get(name=GROUP_NAME_MODERATORS)
        self.user = UserFactory(settings__first_name="Matti",
                                settings__last_name="Meikäläinen")

    def test_moderator(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_moderator)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/")

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkadmin/users_list.html")
        self.assertContains(resp, "Matti Meikäläinen")
        self.assertContains(resp, "Moderaattori")

    def test_admin(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_admin)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/")

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkadmin/users_list.html")
        self.assertContains(resp, "Matti Meikäläinen")
        self.assertContains(resp, "Ylläpitäjä")


class UsersListActionButtonsTest(TestCase):
    """ Tests whether the action button shows up for and on proper users """

    def setUp(self):
        self.group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        self.group_moderator = Group.objects.get(name=GROUP_NAME_MODERATORS)
        self.user = UserFactory()
        self.user_admin = UserFactory()
        self.user_admin.groups.add(self.group_admin)
        self.user_moderator = UserFactory()
        self.user_moderator.groups.add(self.group_moderator)
        self.user_participant = UserFactory()

    def test_moderator(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_moderator)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/")

        self.assertEqual(resp.status_code, 200)
        href_base = "/fi/hallinta/kayttajat/{}/muokkaa/"
        self.assertContains(resp, href_base.format(self.user.pk))
        self.assertNotContains(resp, href_base.format(self.user_admin.pk))
        self.assertNotContains(resp, href_base.format(self.user_moderator.pk))
        self.assertContains(resp, href_base.format(self.user_participant.pk))

    def test_admin(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_admin)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/")

        self.assertEqual(resp.status_code, 200)
        href_base = "/fi/hallinta/kayttajat/{0}/muokkaa/"
        self.assertContains(resp, href_base.format(self.user.pk))
        self.assertContains(resp, href_base.format(self.user_admin.pk))
        self.assertContains(resp, href_base.format(self.user_moderator.pk))
        self.assertContains(resp, href_base.format(self.user_participant.pk))


class UsersListFilterTest(TestCase):

    def setUp(self):
        group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        group_moderator = Group.objects.get(name=GROUP_NAME_MODERATORS)
        user_1 = UserSettingsFactory().user
        user_2 = UserSettingsFactory().user
        user_3 = UserSettingsFactory().user
        user_4 = UserSettingsFactory().user
        user_5 = UserSettingsFactory().user
        user_6 = UserSettingsFactory().user
        user_1.groups.add(group_admin)
        user_2.groups.add(group_admin)
        user_3.groups.add(group_moderator)
        user_4.groups.add(group_moderator)
        user_5.groups.clear()
        user_6.groups.clear()
        self.client.login(username=user_1.username, password=DEFAULT_PASSWORD)

    def test_filter_all(self):
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 6)
        self.assertEqual(user_list[0].groups.first().name, GROUP_NAME_ADMINS)
        self.assertEqual(user_list[1].groups.first().name, GROUP_NAME_ADMINS)
        self.assertEqual(user_list[2].groups.first().name, GROUP_NAME_MODERATORS)
        self.assertEqual(user_list[3].groups.first().name, GROUP_NAME_MODERATORS)
        self.assertEqual(user_list[4].groups.count(), 0)
        self.assertEqual(user_list[5].groups.count(), 0)

    def test_filter_participant(self):
        resp = self.client.get("/fi/hallinta/kayttajat/osallistujat/")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 2)
        self.assertEqual(user_list[0].groups.count(), 0)
        self.assertEqual(user_list[1].groups.count(), 0)

    def test_filter_moderator(self):
        resp = self.client.get("/fi/hallinta/kayttajat/moderaattorit/")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 2)
        self.assertEqual(user_list[0].groups.first().name, GROUP_NAME_MODERATORS)
        self.assertEqual(user_list[1].groups.first().name, GROUP_NAME_MODERATORS)

    def test_filter_admin(self):
        resp = self.client.get("/fi/hallinta/kayttajat/yllapitajat/")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 2)
        self.assertEqual(user_list[0].groups.first().name, GROUP_NAME_ADMINS)
        self.assertEqual(user_list[1].groups.first().name, GROUP_NAME_ADMINS)


class UsersListSearchTest(TestCase):

    def setUp(self):
        user_1 = UserFactory(
            username="masa",
            settings__first_name="Matti",
            settings__last_name="Meikäläinen"
        )
        user_2 = UserFactory(
            username="henu",
            settings__first_name="Henri",
            settings__last_name="Kuisma"
        )
        user_3 = UserFactory(
            username="kalevi1997",
            settings__first_name="Kalevi",
            settings__last_name="Kuusisto"
        )
        organization_1 = Organization.objects.create(name="Helsingin koulu", type=1)
        organization_2 = Organization.objects.create(name="Turun koulu", type=1)
        user_1.organizations.add(organization_1)
        user_2.organizations.add(organization_1)
        user_2.organizations.add(organization_2)
        user_3.organizations.add(organization_2)

        group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        user_1.groups.add(group_admin)
        self.client.login(username=user_1.username, password=DEFAULT_PASSWORD)

    def test_no_needle(self):
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]
        self.assertEqual(len(user_list), 3)

    def test_first_name(self):
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/?" + QS_SEARCH + "=matti")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 1)
        self.assertEqual(user_list[0].settings.first_name, "Matti")

    def test_search_last_name(self):
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/?"
                               + QS_SEARCH + "=kuisma")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 1)
        self.assertEqual(user_list[0].settings.last_name, "Kuisma")

    def test_search_username(self):
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/?"
                               + QS_SEARCH + "=kalevi1997")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 1)
        self.assertEqual(user_list[0].username, "kalevi1997")

    def test_search_organization(self):
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/?"
                               + QS_SEARCH + "=helsingin koulu")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 2)
        self.assertEqual(user_list[0].username, "masa")
        self.assertEqual(user_list[1].username, "henu")

        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/?" + QS_SEARCH + "=turun koulu")
        self.assertEqual(resp.status_code, 200)
        user_list = resp.context["user_list"]

        self.assertEqual(len(user_list), 2)
        self.assertEqual(user_list[0].username, "henu")
        self.assertEqual(user_list[1].username, "kalevi1997")


class UsersListOrderTest(TestCase):

    def setUp(self):
        self.user_1 = UserFactory(
            username="masa",
            settings__first_name="Matti",
            settings__last_name="Meikäläinen",
            settings__municipality=MunicipalityFactory(name_fi="Helsinki")
        )
        self.user_2 = UserFactory(
            username="henu",
            settings__first_name="Henri",
            settings__last_name="Kuisma",
            settings__municipality=MunicipalityFactory(name_fi="Vantaa")
        )
        self.user_3 = UserFactory(
            username="kalevi1997",
            settings__first_name="Kalevi",
            settings__last_name="Kuusisto",
            settings__municipality=MunicipalityFactory(name_fi="Espoo")
        )
        organization_1 = Organization.objects.create(name="Helsingin koulu", type=1)
        organization_2 = Organization.objects.create(name="Turun koulu", type=1)
        self.user_1.organizations.add(organization_1)
        self.user_2.organizations.add(organization_1)
        self.user_2.organizations.add(organization_2)
        self.user_3.organizations.add(organization_2)

        group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        self.user_1.groups.add(group_admin)
        self.client.login(username=self.user_1.username, password=DEFAULT_PASSWORD)

    def test_name(self):
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/?"
                               + QS_ORDER_BY + "=nimi")
        self.assertEqual(resp.status_code, 200)
        user_list = list(resp.context["user_list"])
        expected = [
            self.user_2,
            self.user_3,
            self.user_1
        ]
        self.assertEqual(expected, user_list)

    def test_organizations(self):
        #TODO: Fix sorting and then implement.
        pass

    def test_municipality(self):
        #TODO: Fix this test to pass. The code below does not work for some reason.
        """
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/?"
                               + QS_ORDER_BY + "=kotikunta")
        self.assertEqual(resp.status_code, 200)
        user_list = list(resp.context["user_list"])
        expected = [
            self.user_3, # Espoo
            self.user_1, # Helsinki
            self.user_2  # Vantaa
        ]
        self.assertEqual(expected, user_list)
        """
        pass


class UsersListPaginationTest(TestCase):

    def setUp(self):
        self.users = []
        for i in range(0, 55):
            self.users.append(UserFactory())

        group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        self.users[0].groups.add(group_admin)
        self.client.login(username=self.users[0].username, password=DEFAULT_PASSWORD)

    def test_pages(self):
        resp = self.client.get("/fi/hallinta/kayttajat/kaikki/")
        self.assertEqual(resp.status_code, 200)
        paged_users = resp.context["users"]

        self.assertEqual(paged_users.paginator.num_pages, 2)
        self.assertEqual(paged_users.paginator.count, 55)
        self.assertEqual(paged_users.paginator.page(1).object_list.count(), 50)
        self.assertEqual(paged_users.paginator.page(2).object_list.count(), 5)


class UsersEditUnauthorizedAccessTest(TestCase):

    def setUp(self):
        self.group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        self.group_moderator = Group.objects.get(name=GROUP_NAME_MODERATORS)
        self.user = UserFactory()
        self.user.groups.add(self.group_moderator)
        self.target_user = UserFactory()

    def test_anonymous_redirect(self):
        resp = self.client.get(reverse("nkadmin:users_edit", args=[self.target_user.pk]),
                               follow=True)
        self.assertContains(resp, 'Kirjaudu sisään tai rekisteröidy', status_code=200)

    def test_unauthorized_redirect(self):
        user_logged = UserFactory()
        self.client.login(username=user_logged.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk,
                               follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Ei käyttöoikeutta.')
        self.assertContains(resp, 'Kirjaudu sisään')

    def test_moderator_another_moderator(self):
        self.target_user.groups.clear()
        self.target_user.groups.add(self.group_moderator)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk,
                               follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Ei käyttöoikeutta.')
        self.assertContains(resp, 'Kirjaudu sisään')

    def test_moderator_admin(self):
        self.target_user.groups.clear()
        self.target_user.groups.add(self.group_admin)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk,
                               follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Ei käyttöoikeutta.')
        self.assertContains(resp, 'Kirjaudu sisään')


class UsersEditAuthorizedAccessTest(TestCase):
    """ Tests that moderators and admins can enter the edit forms. Also checks that
        admins don't get the usergroup field. """

    def setUp(self):
        self.group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        self.group_moderator = Group.objects.get(name=GROUP_NAME_MODERATORS)
        self.user = UserSettingsFactory().user
        self.target_user = UserSettingsFactory().user

    def test_moderator_self(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_moderator)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.user.pk)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkadmin/edit_user.html")
        self.assertNotContains(resp, 'Käyttäjäryhmät')

    def test_moderator_participant(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_moderator)
        self.target_user.groups.clear()
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkadmin/edit_user.html")
        self.assertNotContains(resp, 'Käyttäjäryhmät')

    def test_admin_self(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_admin)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.user.pk)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkadmin/edit_user.html")
        self.assertContains(resp, 'Käyttäjäryhmät')

    def test_admin_participant(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_admin)
        self.target_user.groups.clear()
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkadmin/edit_user.html")
        self.assertContains(resp, 'Käyttäjäryhmät')

    def test_admin_moderator(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_admin)
        self.target_user.groups.clear()
        self.target_user.groups.add(self.group_moderator)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkadmin/edit_user.html")
        self.assertContains(resp, 'Käyttäjäryhmät')

    def test_admin_admin(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_admin)
        self.target_user.groups.clear()
        self.target_user.groups.add(self.group_admin)
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkadmin/edit_user.html")
        self.assertContains(resp, 'Käyttäjäryhmät')


class UsersEditSavesTest(TestCase):

    def setUp(self):
        self.group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        self.user = UserSettingsFactory().user
        self.user.groups.add(self.group_admin)
        self.target_user = UserSettingsFactory().user
        self.municipality = MunicipalityFactory(name_fi='Espoo')
        self.organization1 = Organization.objects.first()
        self.organization2 = Organization.objects.last()

    def test_save(self):
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post(
            "/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk,
            {
                'user-username': "meme",
                "user-status": str(User.STATUS_ARCHIVED),
                "user-organizations": [str(self.organization1.pk),
                                       str(self.organization2.pk)],
                'usersettings-first_name': "Teppo",
                'usersettings-last_name': "Testaaja",
                'usersettings-birth_date': "06.03.2001",
                'usersettings-municipality': str(self.municipality.pk),
                'usersettings-email': "me@example.com",
                'usersettings-phone_number': "+35812345494",
            },
            follow=True
        )

        target_user = User.objects.get(pk=self.target_user.id)
        self.assertEqual(target_user.username, "meme")
        self.assertEqual(target_user.status, User.STATUS_ARCHIVED)
        self.assertListEqual(
            list(target_user.organizations.all()),
            [self.organization1, self.organization2]
        )
        self.assertEqual(target_user.settings.first_name, "Teppo")
        self.assertEqual(target_user.settings.last_name, "Testaaja")
        self.assertEqual(
            target_user.settings.birth_date
                .strftime(u"%d.%m.%Y".decode("utf-8")).encode("utf-8"),
            "06.03.2001"
        )
        self.assertEqual(
            target_user.settings.municipality,
            self.municipality
        )
        self.assertEqual(target_user.settings.message_notification, False)
        self.assertEqual(target_user.settings.email, "me@example.com")
        self.assertEqual(target_user.settings.phone_number, "+35812345494")

    def test_missing_fields(self):
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post(
            "/fi/hallinta/kayttajat/%d/muokkaa/" % self.target_user.pk, {}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Tämä kenttä vaaditaan', 5)

    def test_invalid_username(self):
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post("/fi/hallinta/kayttajat/%d/muokkaa/" %
                                self.target_user.pk,
                                {'user-username': 'meatexample.com'})
        self.assertContains(resp, 'Syötä kelvollinen käyttäjätunnus.', 1)

    def test_invalid_phone(self):
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post("/fi/hallinta/kayttajat/%d/muokkaa/" %
                                self.target_user.pk,
                                {'usersettings-phone_number': '050 123 1234'})
        self.assertContains(resp, 'Syötä puhelinnumero kansainvälisessä muodossa', 1)

    # TODO: Should admins/moderators be forbidden to change email to one that is in use?
    """
    def test_email_already_in_use(self):
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        UserFactory(settings__email='joku@example.com')
        resp = self.client.post("/fi/hallinta/kayttajat/%d/muokkaa/" %
                                self.target_user.pk,
                                {'usersettings-email': 'joku@example.com'})
        self.assertContains(resp, 'Sähköpostiosoite on jo käytössä.')
    """
