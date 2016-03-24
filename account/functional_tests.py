# coding=utf-8

from __future__ import unicode_literals

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.test import LiveServerTestCase

from .factories import UserSettingsFactory, UserFactory, DEFAULT_PASSWORD
from .models import User


class AccountRegistrationTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def get_element_attr_by_id(self, el_id, attr):
        element = self.browser.find_element_by_id(el_id)
        return element.get_attribute(attr)

    def test_sign_up_confirmation_method_js(self):
        self.browser.get(self.live_server_url + '/kayttaja/rekisteroidy/')

        # confirmation method is email by default
        self.assertEqual(
            self.get_element_attr_by_id('id_usersettings-confirmation_method_0', 'checked'),
            'true'
        )

        # phone number input is hidden in that case
        self.assertEqual(
            self.get_element_attr_by_id('id_usersettings-phone_number_wrap', 'style'),
            'display: none;'
        )

        # change confirmation method to sms
        self.browser.find_element_by_id('id_usersettings-confirmation_method_1').click()

        # phone number input gets visible
        self.assertEqual(
            self.get_element_attr_by_id('id_usersettings-phone_number_wrap', 'style'),
            'display: block;'
        )

        # test login and registration links
        base_url = self.live_server_url
        self.browser.get(base_url)

        self.browser.find_element_by_link_text('Rekisteröidy').click()
        self.assertEqual(
            self.browser.current_url,
            base_url + '/kayttaja/valitse-rekisteroitymistapa/'
        )

        self.browser.find_element_by_id('nk-rekisteroityminen').click()
        self.assertEqual(
            self.browser.current_url,
            base_url + '/kayttaja/rekisteroidy/'
        )

        self.browser.find_element_by_link_text('Kirjaudu sisään').click()
        self.assertEqual(
            self.browser.current_url,
            base_url + '/kayttaja/kirjaudu-sisaan/'
        )


class AccountSettingsTest(LiveServerTestCase):

    def fill_input(self, el_id, text, enter=False):
        input_box = self.browser.find_element_by_id(el_id)
        input_box.send_keys(text)
        if enter:
            input_box.send_keys(Keys.ENTER)

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

        self.user = UserFactory(is_active=True, status=User.STATUS_ACTIVE)
        self.browser.get(self.live_server_url + '/kayttaja/kirjaudu-sisaan/')
        self.fill_input('id_username', self.user.username)
        self.fill_input('id_password', DEFAULT_PASSWORD, True)

    def tearDown(self):
        self.browser.quit()
        pass

    def test_updating_user_settings(self):
        settings_link = self.browser.find_element_by_link_text('@' + self.user.username)
        self.assertEqual(
            settings_link.get_attribute('href'),
            self.live_server_url + '/kayttaja/{}/'.format(self.user.pk)
        )
        settings_link.click()

        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + '/kayttaja/{}/asetukset/'.format(self.user.pk)
        )

