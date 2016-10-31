# coding=utf-8

from __future__ import unicode_literals

import json
import os
from datetime import timedelta
from django.contrib.auth.models import Group

from django.core import mail
from django.core.files.base import File
from django.core.management import call_command
from django.test.utils import override_settings
from account.models import GROUP_NAME_ADMINS, GROUP_NAME_MODERATORS
from content.factories import IdeaFactory
from content.models import Idea
from favorite.models import Favorite

from nuka.test.testcases import TestCase
from account.factories import UserFactory
from account.forms import EmailConfirmationForm, UserSignUpForm
from organization.factories import MunicipalityFactory, OrganizationFactory

from .models import User, UserSettings
from .factories import UserSettingsFactory, DEFAULT_PASSWORD


@override_settings(SMS={'enabled': False})
class SignupTest(TestCase):

    def setUp(self):
        self.municipality = MunicipalityFactory(name_fi='Espoo')

    def register_user(self, confirmation_method=UserSignUpForm.CONFIRMATION_CHOICE_EMAIL,
                      follow=True):
        response = self.client.post('/fi/kayttaja/rekisteroidy/', {
                'user-username': 'meme',
                'user-password1': 'testi123',
                'user-password2': 'testi123',
                'usersettings-first_name': 'Teppo',
                'usersettings-last_name': 'Testaaja',
                'usersettings-phone_number': '+35812345494',
                'usersettings-email': 'me@example.com',
                'usersettings-confirmation_method': confirmation_method,
                'usersettings-birth_date': '1.1.2001',
                'usersettings-municipality': str(self.municipality.pk)
            },
            follow=follow)

        self.assertNotContains(response, 'Valitse oikea vaihtoehto', msg_prefix='Väärä municipal')
        signup_data = response.context['request'].session['sign_up']
        return {'response': response, 'signup_data': signup_data}

    def get_wrong_pin_activation_response(self, follow=False):
        wrong_pin = '1234'
        reg_data = self.register_user()

        if wrong_pin == reg_data['signup_data']['pin_code']:
            wrong_pin = '2345'

        return self.client.post('/fi/kayttaja/aktivoi/', {
            'pin_code': wrong_pin
        }, follow=follow)

    def test_rekisteroitymisvalintalomakkeen_avaaminen(self):
        resp = self.client.get('/fi/kayttaja/valitse-rekisteroitymistapa/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Rekisteröidy sähköpostiosoitteella')
        self.assertTemplateUsed(resp, 'account/signup_choices.html')
        self.assertTemplateNotUsed(resp, 'account/signup.html')

    def test_rekisteroitymislomakkeen_avaaminen(self):
        resp = self.client.get('/fi/kayttaja/rekisteroidy/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Salasana')
        self.assertTemplateUsed(resp, 'account/signup.html')
        self.assertTemplateNotUsed(resp, 'account/login.html')

    def test_successful_signup(self):
        # Mr. Play-It-Safe
        # TODO test sms

        self.assertEqual(len(mail.outbox), 0)
        reg_data = self.register_user()

        user = User.objects.filter(pk=reg_data['signup_data']['user_id'])
        self.assertEqual(user.count(), 1)

        resp = reg_data['response']
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/signup_activation.html')
        self.assertContains(resp, 'Vahvista rekisteröityminen')

        user = User.objects.get(username='meme')
        self.assertEqual(user.status, User.STATUS_AWAITING_ACTIVATION)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.settings.email, 'me@example.com')
        self.assertEqual(user.settings.first_name, 'Teppo')
        self.assertEqual(user.settings.last_name, 'Testaaja')
        self.assertEqual(user.settings.phone_number, '+35812345494')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], 'me@example.com')
        self.assertEqual(mail.outbox[0].subject, "Vahvista sähköpostiosoitteesi")
        self.assertFalse('{%' in mail.outbox[0].body)

    def test_wrong_pin_code(self):
        response = self.get_wrong_pin_activation_response()
        self.assertContains(response, 'Virheellinen vahvistustunnus')
        self.assertTemplateUsed(response, 'account/signup_activation.html')

    def test_too_many_retries(self):
        reg_data = self.register_user()
        self.assertEqual(len(reg_data['signup_data']['pin_code']), 4)

        # try activate 4 times with wrong pin
        for x in range(0, 4):
            self.get_wrong_pin_activation_response()

        # 5th time
        response = self.get_wrong_pin_activation_response(True)
        self.assertContains(response, 'Aktivointiyritykset käytetty. Rekisteröidy uudelleen.', status_code=200)
        self.assertTemplateUsed(response, 'account/signup.html')

        user = User.objects.filter(pk=reg_data['signup_data']['user_id'])
        self.assertEqual(user.count(), 0)

    def test_activate_user(self):
        reg_data = self.register_user()
        resp = self.client.post('/fi/kayttaja/aktivoi/',
                                {'pin_code': reg_data['signup_data']['pin_code']},
                                follow=True)
        self.assertTemplateUsed(resp, 'account/signup_activated.html')

    def test_try_activate_when_session_missing(self):
        resp = self.client.get('/fi/kayttaja/aktivoi/', follow=True)
        self.assertTemplateUsed(resp, 'account/signup.html')

    def test_missing_fields(self):
        resp = self.client.post('/fi/kayttaja/rekisteroidy/', {})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Tämä kenttä vaaditaan', 8)

    def test_invalid_username(self):
        resp = self.client.post('/fi/kayttaja/rekisteroidy/',
                                {'user-username': 'meatexample.com'})
        self.assertContains(resp, 'Syötä kelvollinen käyttäjätunnus.', 1)

    def test_invalid_phone(self):
        resp = self.client.post('/fi/kayttaja/rekisteroidy/',
                                {'usersettings-phone_number': '050 123 1234'})
        self.assertContains(resp, 'Syötä puhelinnumero kansainvälisessä muodossa', 1)

    def test_email_already_in_use(self):
        UserFactory(settings__email='joku@example.com')
        resp = self.client.post('/fi/kayttaja/rekisteroidy/',
                                {'usersettings-email': 'joku@example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/signup.html')
        self.assertTemplateNotUsed(resp, 'account/signup_activation.html')
        self.assertContains(resp, 'Sähköpostiosoite on jo käytössä.')


class EmailConfirmation(TestCase):
    def test_vahvista_sahkoposti(self):
        user = UserFactory(status=User.STATUS_AWAITING_ACTIVATION)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(user.is_active)
        token = EmailConfirmationForm.create_token(user)

        resp = self.client.get('/fi/kayttaja/vahvista-sahkoposti/%s/' % token)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/email_confirmed.html')
        self.assertContains(resp, 'Sähköposti vahvistettu')
        self.assertEqual(len(mail.outbox), 0)

    def test_broken_activation_link(self):
        user = UserFactory(is_active=False, status=User.STATUS_AWAITING_ACTIVATION)
        token = EmailConfirmationForm.create_token(user)
        resp = self.client.get('/fi/kayttaja/vahvista-sahkoposti/%s/' % token[1:])
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/email_confirmation_failed.html')
        self.assertContains(resp, 'Vahvistuslinkki on virheellinen tai vanhentunut.')

    def test_invalid_activation_link(self):
        resp = self.client.get(
            '/fi/kayttaja/vahvista-sahkoposti/abrakadabrsentaytyytoimiamutmitjoseitoimi/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/email_confirmation_failed.html')
        self.assertContains(resp, 'Vahvistuslinkki on virheellinen tai vanhentunut.')


class LoginTest(TestCase):
    def test_show_login_form(self):
        resp = self.client.get('/fi/kayttaja/kirjaudu-sisaan/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/login.html')
        self.assertContains(resp, 'Salasana')
        self.assertContains(resp, 'Käyttäjänimi')

    def test_active_user_login(self):
        user = UserFactory(username='Tepotin')
        resp = self.client.post('/fi/kayttaja/kirjaudu-sisaan/', {
            'username': user.username,
            'password': DEFAULT_PASSWORD
        }, follow=True)
        self.assertRedirects(resp, '/fi/kayttaja/{}/'.format(user.pk))
        self.assertContains(resp, 'Tepotin')
        self.assertNotContains(resp, "Ei käyttöoikeutta")

    def test_bad_username(self):
        resp = self.client.post('/fi/kayttaja/kirjaudu-sisaan/', {
            'username': 'ei-ole-tammoista',
            'password': DEFAULT_PASSWORD
        }, follow=True)
        self.assertContains(resp, "Virheellinen käyttäjätunnus tai salasana.",
                            status_code=200)

    def test_inactive_user(self):
        k1 = UserFactory(status=User.STATUS_AWAITING_ACTIVATION)
        k2 = UserFactory(status=User.STATUS_ARCHIVED)
        for user in (k1, k2, ):
            resp = self.client.post('/fi/kayttaja/kirjaudu-sisaan/', {
                'username': user.username,
                'password': DEFAULT_PASSWORD
            }, follow=True)
            self.assertContains(resp, "Käyttäjätunnus ei ole aktiivinen.",
                                status_code=200)

    def test_welcome_messages(self):
        user = UserFactory()
        resp = self.client.post('/fi/kayttaja/kirjaudu-sisaan/', {
            'username': user.username,
            'password': DEFAULT_PASSWORD
        }, follow=True)
        self.assertRedirects(resp, '/fi/kayttaja/{}/'.format(user.pk),
                             target_status_code=200)
        self.assertNotContains(resp, 'Käytit palvelua viimeksi')
        self.assertContains(resp, 'Tervetuloa Nuortenideat.fi palveluun!')
        user.joined -= timedelta(seconds=5)
        user.save()
        resp = self.client.post('/fi/kayttaja/kirjaudu-sisaan/', {
            'username': user.username,
            'password': DEFAULT_PASSWORD
        }, follow=True)
        self.assertContains(resp, 'Käytit palvelua viimeksi')
        self.assertNotContains(resp, 'Tervetuloa Nuortenideat.fi palveluun!')


class LogoutTest(TestCase):
    def test_kirjaudu_ulos(self):
        user = UserFactory()
        self.client.login(username=user.username,
                          password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/kayttaja/kirjaudu-ulos/', follow=True, target_status_code=200)
        self.assertContains(resp, 'Sinut on kirjattu ulos palvelusta')


class CreateSuperuserCommandLineTest(TestCase):
    def test_luo_paakattaja(self):
        self.assertEqual(User.objects.count(), 0)
        call_command('createsuperuser', verbosity=0, interactive=False,
                     username='paakkis123')
        k = User.objects.get(username='paakkis123')
        self.assertTrue(k.is_active)
        self.assertTrue(k.is_superuser)
        self.assertTrue(k.is_staff)


class MyAccountTest(TestCase):
    def setUp(self):
        self.settings = UserSettingsFactory(first_name='Kyösti Kullervo')
        self.user = self.settings.user
        self.client.login(username=self.user.username,
                          password=DEFAULT_PASSWORD)

    def test_user_settings_template(self):
        resp = self.client.get('/fi/kayttaja/{}/asetukset/'.format(self.user.pk))
        self.assertTemplateUsed(resp, 'account/user_settings.html')

    def test_open_edit_user_settings(self):
        resp = self.client.get('/fi/kayttaja/{}/muokkaa-asetukset/'.format(self.user.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/user_settings_edit.html')
        self.assertContains(resp, 'value="Kyösti Kullervo"')

    def test_open_display_user_settings(self):
        resp = self.client.get('/fi/kayttaja/{}/nayta-asetukset/'.format(self.user.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/user_settings_detail.html')
        self.assertContains(resp, '<p>Kyösti Kullervo</p>')


class ProfilePictureTest(TestCase):
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'nuka', 'testdata', 'lolcat-sample.jpg')

    def setUp(self):
        self.user = UserSettingsFactory().user
        self.client.login(username=self.user.username,
                          password=DEFAULT_PASSWORD)

    def test_upload_main_pic(self):
        self.assertRaises(ValueError, lambda: self.user.settings.picture.file)
        resp = self.client.post('/fi/kayttaja/%d/asetukset/kuva/muokkaa/' % self.user.pk, {
            'picture': open(self.test_file, 'rb')
        })
        self.assertEqual(resp.status_code, 200)
        settings = UserSettings.objects.get(user=self.user)
        self.assertTrue(settings.picture.url.endswith('.jpg'))
        self.assertTrue(settings.picture_medium.url.endswith('.jpg'))
        self.assertTrue(settings.picture_small.url.endswith('.jpg'))

    def test_open_edit_picture_fragment(self):
        resp = self.client.get('/fi/kayttaja/%d/asetukset/kuva/muokkaa/' % self.user.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/profile_picture_form.html')
        self.assertTemplateUsed(resp, 'nuka/inline_edit_base_form.html')
        self.assertContains(resp, "Valitse kuva")

    def test_open_picture_fragment_no_existing_pic(self):
        resp = self.client.get('/fi/kayttaja/%d/asetukset/kuva/' % self.user.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/user_settings_picture.html')
        self.assertContains(resp, "profile_pic_placeholder")

    def test_open_picture_fragment_with_existing_pic(self):
        self.user.settings.picture.save('lolcat.jpg', File(open(self.test_file, 'rb')))
        resp = self.client.get('/fi/kayttaja/%d/asetukset/kuva/' % self.user.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'account/user_settings_picture.html')
        self.assertNotContains(resp, "profile_pic_placeholder")
        self.assertContains(resp, '<img')
        self.assertContains(resp, self.user.settings.picture_medium.url)

    def test_open_picture_fragment_with_existing_pic(self):
        self.user.settings.picture.save('lolcat.jpg', File(open(self.test_file, 'rb')))
        resp = self.client.delete('/fi/kayttaja/%d/asetukset/kuva/poista/' % self.user.pk)
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue(resp['success'])
        self.assertEqual(resp['next'], '/fi/kayttaja/%d/asetukset/kuva/' % self.user.pk)
        settings = UserSettings.objects.get(pk=self.user.settings.pk)
        self.assertRaises(ValueError, lambda: settings.picture.file)

    def tearDown(self):
        settings = UserSettings.objects.get(user__pk=self.user.pk)
        settings.picture.delete()


class ProfileInitiativesListTest(TestCase):
    def setUp(self):
        self.user1 = UserSettingsFactory().user
        self.user2 = UserSettingsFactory().user
        self.admin = UserFactory(groups=[
            Group.objects.get(name=GROUP_NAME_ADMINS)
        ])
        self.moderator = UserFactory(groups=[
            Group.objects.get(name=GROUP_NAME_MODERATORS)
        ])
        self.idea1 = IdeaFactory(owners=[self.user1],
                                 title="Public Initiative",
                                 visibility=Idea.VISIBILITY_PUBLIC)
        IdeaFactory(owners=[self.user1, self.user2],
                    title="Shared Initiative",
                    visibility=Idea.VISIBILITY_DRAFT)
        IdeaFactory(owners=[self.user1],
                    title="Draft Initiative",
                    visibility=Idea.VISIBILITY_DRAFT)
        IdeaFactory(owners=[self.user2],
                    title="Non-Owned Initiative",
                    visibility=Idea.VISIBILITY_DRAFT)

    def test_show_public_initiatives_as_guest(self):
        resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Public Initiative")
        self.assertNotContains(resp, "Draft Initiative")
        self.assertNotContains(resp, "Shared Initiative")
        self.assertNotContains(resp, "Non-Owned Initiative")

    def test_show_all_initiatives_as_owner(self):
        self.client.login(username=self.user1.username,
                          password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
        self.assertContains(resp, "Public Initiative", count=1)
        self.assertContains(resp, "Draft Initiative", count=1)
        self.assertContains(resp, "Shared Initiative", count=1)
        self.assertNotContains(resp, "Non-Owned Initiative")

    def test_show_all_initiatives_as_admin(self):
        self.client.login(username=self.admin.username,
                          password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
        self.assertContains(resp, "Public Initiative", count=1)
        self.assertContains(resp, "Draft Initiative", count=1)
        self.assertContains(resp, "Shared Initiative", count=1)
        self.assertNotContains(resp, "Non-Owned Initiative")

    def test_show_all_initiatives_as_moderator(self):
        self.client.login(username=self.moderator.username,
                          password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
        self.assertContains(resp, "Public Initiative", count=1)
        self.assertContains(resp, "Draft Initiative", count=1)
        self.assertContains(resp, "Shared Initiative", count=1)
        self.assertNotContains(resp, "Non-Owned Initiative")

    def test_show_public_and_co_owned_initiatives(self):
        self.client.login(username=self.user2.username,
                          password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
        self.assertContains(resp, "Public Initiative", count=1)
        self.assertContains(resp, "Shared Initiative", count=1)
        self.assertNotContains(resp, "Draft Initiative")
        self.assertNotContains(resp, "Non-Owned Initiative")

    def test_no_dupe_initiatives_as_guest_if_multiple_owners(self):
        self.idea1.owners.add(UserFactory())
        resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
        self.assertContains(resp, "Public Initiative", count=1)

    def test_organization_initiatives_show_organization_name_as_owner(self):
        organization = OrganizationFactory(admins=[self.user1])
        idea = IdeaFactory(owners=[], initiator_organization=organization)
        Favorite.objects.create(user=self.user1, content_object=idea)

        self.client.login(username=self.user1.username, password=DEFAULT_PASSWORD)
        resp = self.client.get(
            '/fi/kayttaja/%d/lista/?initiative_ct_id=&ct_natural_key=content.idea' %
            self.user1.pk
        )
        self.assertContains(resp, organization.name, count=1)


class ProfilePageVisibilityTest(TestCase):
    def setUp(self):
        self.user1 = UserSettingsFactory().user
        contact_user = UserSettingsFactory().user
        self.organization = OrganizationFactory(admins=[contact_user,])
        self.contact_user = User.objects.get(pk=contact_user.pk)
        self.admin = UserFactory(groups=[
            Group.objects.get(name=GROUP_NAME_ADMINS)
        ])

    def test_view_user_profile_not_authenticated(self):
        resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
        self.assertTemplateUsed(resp, 'account/user_profile_public.html')

        self.assertNotContains(resp, '<li>Yhteyshenkilö:')
        self.assertNotContains(resp, 'Lähetä käyttäjälle viesti')
        self.assertNotContains(resp, "{} {}".format(self.user1.settings.first_name,
                                                    self.user1.settings.last_name))
        self.assertNotContains(resp, '<img class="profile-organization-picture')
        self.assertNotContains(resp, '<img class="org-admin-online-status')

        self.assertContains(resp, '<div class="no-picture-bar-magenta">')

    def test_view_contact_user_profile_not_authenticated(self):
        resp = self.client.get('/fi/kayttaja/%d/' % self.contact_user.pk)
        self.assertTemplateUsed(resp, 'account/user_profile_public.html')

        self.assertNotContains(resp, 'Lähetä käyttäjälle viesti')

        self.assertContains(resp, '<li>Yhteyshenkilö:')
        self.assertContains(resp, '<div class="no-picture-bar-blue">')
        self.assertContains(resp, self.contact_user.get_full_name())

    def test_view_contact_user_profile_authenticated(self):
        self.client.login(username=self.user1.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/kayttaja/%d/' % self.contact_user.pk)
        self.assertTemplateUsed(resp, 'account/user_profile_public.html')

        self.assertNotContains(resp, '<li>Seuratut aiheet:')
        self.assertNotContains(resp, '<li>Seuratut organisaatiot:')

        self.assertContains(resp, 'Lähetä käyttäjälle viesti')

    # def test_view_user_profile_as_admin(self):
    #    self.client.login(username=self.admin.username, password=DEFAULT_PASSWORD)
    #    resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
    #    self.assertTemplateUsed(resp, 'account/user_profile.html')
    #    self.assertNotContains(resp, '<li>Seuratut aiheet:')
    #    self.assertNotContains(resp, '<li>Seuratut organisaatiot:')
    #
    #    self.assertContains(resp, 'Profiili</h1>')

    def test_view_own_profile(self):
        self.client.login(username=self.user1.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/kayttaja/%d/' % self.user1.pk)
        self.assertTemplateUsed(resp, 'account/user_profile.html')
        self.assertContains(resp, '<li>Seuratut aiheet:')
        self.assertContains(resp, '<li>Seuratut organisaatiot:')
        self.assertContains(resp, 'Oma sivu</h1>')
