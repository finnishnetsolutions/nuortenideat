# coding=utf-8

from __future__ import unicode_literals

import json
import os
from datetime import timedelta, date
from unittest.case import skipUnless

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.files.base import File, ContentFile
from django.test.utils import override_settings

from account.factories import UserFactory, DEFAULT_PASSWORD
from account.models import GROUP_NAME_MODERATORS
from content.utils import warn_unpublished, archive_unpublished, remind_untransferred, \
    warn_untransferred, archive_untransferred
from content.tasks import (warn_unpublished as warn_unpublished_task,
                           archive_unpublished as archive_unpublished_task,
                           remind_untransferred as remind_untransferred_task,
                           warn_untransferred as warn_untransferred_task,
                           archive_untransferred as archive_untransferred_task)
from libs.attachtor.models.models import Upload, UploadGroup
from libs.attachtor.utils import get_upload_signature
from nkcomments.models import CustomComment
from nkcomments.factories import CustomCommentFactory
from nkmoderation.models import ModerationReason
from nuka.test.testcases import TestCase

from organization.factories import OrganizationFactory
from organization.models import Organization

from .forms import CreateIdeaForm, EditInitiativeDescriptionForm, IdeaSearchForm
from .factories import IdeaFactory, AdditionalDetailFactory, QuestionFactory
from .models import Initiative, Idea, AdditionalDetail, Question
from tagging.factories import TagFactory


class CreateIdeaAnonymousTest(TestCase):
    def test_anonymous_redirect(self):
        resp = self.client.get('/fi/ideat/uusi/', follow=True)
        self.assertContains(resp, 'Kirjaudu sisään tai rekisteröidy', status_code=200)


class CreateIdeaTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)

    def test_open_create_form(self):
        resp = self.client.get('/fi/ideat/uusi/')
        self.assertContains(resp, '<h1>Uusi idea', status_code=200)

    def test_create_draft(self):
        org1 = OrganizationFactory()
        org2 = OrganizationFactory()
        self.assertEqual(Initiative.objects.count(), 0)
        resp = self.client.post('/fi/ideat/uusi/', {
            'title-fi': "Attachments everywhere!",
            'upload_ticket': get_upload_signature(),
            'description-fi': "Attachments everywhere!",
            'target_type': CreateIdeaForm.TARGET_TYPE_UNKNOWN,
            'target_organizations': [org1.pk, org2.pk],
            'owners': [self.user.pk, ],
            'interaction': Initiative.INTERACTION_EVERYONE,
        })

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Initiative.objects.count(), 1)
        self.assertEqual(Idea._default_manager.count(), 1)
        self.assertEqual(Idea.objects.count(), 0)
        obj = Initiative.objects.first()
        self.assertRedirects(resp, '/fi/ideat/%d/' % obj.pk)
        self.assertEqual(obj.creator, self.user)
        self.assertEqual(obj.visibility, Initiative.VISIBILITY_DRAFT)
        self.assertEqual(obj.target_organizations.count(), 1)
        self.assertEqual(obj.target_organizations.first().type,
                         Organization.TYPE_UNKNOWN)
        self.assertEqual(obj.tags.count(), 0)
        self.assertEqual(obj.owners.count(), 1)

    def test_creator_not_owner(self):
        user2 = UserFactory()
        org = OrganizationFactory()
        self.assertEqual(Initiative.objects.count(), 0)
        resp = self.client.post('/fi/ideat/uusi/', {
            'title': "Attachments everywhere!",
            'target_organizations': [org.pk],
            'owners': [user2.pk]
        })
        self.assertContains(resp, 'Et voi poistaa itseäsi idean omistajista.',
                            status_code=200)


class DeleteIdeaTest(TestCase):
    def test_delete_draft(self):
        idea = IdeaFactory(
            status=Idea.STATUS_DRAFT,
            visibility=Idea.VISIBILITY_DRAFT,
            title="A great idea"
        )
        user = idea.owners.first()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post("/fi/ideat/{0}/poista/".format(idea.pk), follow=True)
        self.assertRedirects(resp, "/fi/selaa/")
        self.assertContains(resp, "Idea '{0}' on poistettu.".format(idea.title))

        with self.assertRaises(Idea.DoesNotExist):
            Idea.objects.get(pk=idea.pk)

    def test_delete_published(self):
        idea = IdeaFactory(
            status=Idea.STATUS_PUBLISHED,
            visibility=Idea.VISIBILITY_PUBLIC,
            title="A great idea"
        )
        user = idea.owners.first()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post("/fi/ideat/{0}/poista/".format(idea.pk), follow=True)
        self.assertRedirects(resp, "/fi/selaa/")
        self.assertContains(resp, "Idea '{0}' on poistettu.".format(idea.title))

        with self.assertRaises(Idea.DoesNotExist):
            Idea.objects.get(pk=idea.pk)

    def test_delete_locked_by_comment(self):
        idea = IdeaFactory(
            status=Idea.STATUS_PUBLISHED,
            visibility=Idea.VISIBILITY_PUBLIC,
            title="A great idea"
        )
        CustomComment.objects.create(
            site_id=1,
            content_type=ContentType.objects.get_for_model(Idea),
            object_pk=idea.pk,
            user_name="Commenter",
            comment="I agree with this."
        )
        user = idea.owners.first()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post("/fi/ideat/{0}/poista/".format(idea.pk), follow=True)
        self.assertRedirects(resp, "/fi/kayttaja/kirjaudu-sisaan/")
        self.assertContains(resp, "Ei käyttöoikeutta.")
        idea_again = Idea.objects.get(pk=idea.pk)
        self.assertEqual(idea, idea_again)

    def test_delete_locked_by_vote(self):
        idea = IdeaFactory(
            status=Idea.STATUS_PUBLISHED,
            visibility=Idea.VISIBILITY_PUBLIC,
            title="A great idea"
        )
        self.client.post("/fi/ideat/{0}/kannata/".format(idea.pk), **{
            "HTTP_USER_AGENT": "test-agent",
            "REMOTE_ADDRE": "127.0.0.1"
        })
        user = idea.owners.first()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post("/fi/ideat/{0}/poista/".format(idea.pk), follow=True)
        self.assertRedirects(resp, "/fi/kayttaja/kirjaudu-sisaan/")
        self.assertContains(resp, "Ei käyttöoikeutta.")
        idea_again = Idea.objects.get(pk=idea.pk)
        self.assertEqual(idea, idea_again)


class PublishIdeaTest(TestCase):
    def test_publish(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           visibility=Idea.VISIBILITY_DRAFT)
        user = idea.owners.first()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post('/fi/ideat/%d/julkaise/' % idea.pk, {}, follow=True)

        #self.assertRedirects(resp, '/fi/ideat/%d/' % idea.pk)
        #self.assertContains(resp, "Idea on julkaistu! Voit vielä muokata ideaa, kunnes "
        #                          "siihen tulee ensimmäinen kannanotto tai kommentti.")
        i2 = Idea.objects.get(pk=idea.pk)
        self.assertEqual(i2.status, Idea.STATUS_PUBLISHED)
        self.assertEqual(i2.visibility, Idea.VISIBILITY_PUBLIC)
        self.assertIsNotNone(i2.published)

    def test_republish(self):
        idea = IdeaFactory(status=Idea.STATUS_PUBLISHED,
                           visibility=Idea.VISIBILITY_PUBLIC)
        user = idea.owners.first()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.post('/fi/ideat/%d/julkaise/' % idea.pk, {}, follow=True)
        self.assertRedirects(resp, '/fi/ideat/%d/' % idea.pk)
        self.assertContains(resp, 'Idea on jo julkaistu.')


class IdeaDetailTest(TestCase):
    def test_open_draft_as_owner(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           visibility=Idea.VISIBILITY_DRAFT)
        user = idea.owners.all()[0]
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/ideat/%d/' % idea.pk)
        self.assertContains(resp, idea.title, status_code=200)
        self.assertContains(resp, 'Julkaise idea</a>')
        self.assertTemplateUsed(resp, 'content/idea_detail.html')

    def test_draft_elements_visibility(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           visibility=Idea.VISIBILITY_DRAFT)
        user = idea.owners.all()[0]
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/ideat/%d/' % idea.pk)
        self.assertNotContains(resp, '<button type="submit" id="vote-support-idea"')
        self.assertNotContains(resp, '<aside id="idea-share-buttons" class="well">')
        self.assertNotContains(resp, '<div class="flag-content')
        self.assertNotContains(resp, '<div class="row initiative-stats-row">')

    def test_transferred_elements_visibility(self):
        idea = IdeaFactory(status=Idea.STATUS_TRANSFERRED,
                           visibility=Idea.VISIBILITY_PUBLIC)
        user = idea.owners.all()[0]
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/ideat/%d/' % idea.pk)
        self.assertNotContains(resp, '<button type="submit" id="vote-support-idea"')
        self.assertContains(resp, '<aside id="idea-share-buttons" class="well">')
        self.assertContains(resp, '<div class="flag-content')
        self.assertContains(resp, '<div class="initiative-stats-row">')

    def test_published_elements_visibility(self):
        idea = IdeaFactory(status=Idea.STATUS_PUBLISHED,
                           visibility=Idea.VISIBILITY_PUBLIC)
        user = idea.owners.all()[0]
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/ideat/%d/' % idea.pk)
        self.assertContains(resp, '<button type="submit" id="vote-support-idea"')
        self.assertContains(resp, '<aside id="idea-share-buttons" class="well">')
        self.assertContains(resp, '<div class="flag-content')
        self.assertContains(resp, '<div class="initiative-stats-row">')

    def test_open_draft_as_non_owner(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           visibility=Idea.VISIBILITY_DRAFT)
        user = UserFactory()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/ideat/%d/' % idea.pk, follow=True)
        self.assertRedirects(resp, '/fi/selaa/')
        self.assertContains(resp, 'Idea ei ole vielä julkinen.')

    def test_open_draft_as_guest(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           visibility=Idea.VISIBILITY_DRAFT)
        resp = self.client.get('/fi/ideat/%d/' % idea.pk, follow=True)
        self.assertRedirects(resp,
                             '/fi/kayttaja/kirjaudu-sisaan/?next=/fi/ideat/%d/' % idea.pk)
        self.assertContains(resp, 'Idea ei ole vielä julkinen. '
                                  'Kirjaudu sisään, jos olet idean omistaja.')

    def test_open_published_idea_as_guest(self):
        idea = IdeaFactory(title="Great Idea #388",
                           status=Idea.STATUS_PUBLISHED,
                           visibility=Idea.VISIBILITY_PUBLIC)
        resp = self.client.get('/fi/ideat/%d/' % idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<title>Idea: Great Idea #388')
        self.assertContains(resp, '<h1 class="h2-style">Great Idea #388')
        self.assertNotContains(resp, '/muokkaa/')
        self.assertNotContains(resp, 'Julkaise idea')

    def test_open_published_idea_as_owner(self):
        idea = IdeaFactory(title="Great Idea #388",
                           status=Idea.STATUS_PUBLISHED,
                           visibility=Idea.VISIBILITY_PUBLIC)
        user = idea.owners.all()[0]
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get('/fi/ideat/%d/' % idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<h1 class="h2-style">Great Idea #388')
        self.assertContains(resp, '/fi/ideat/%d/muokkaa/' % idea.pk, count=1)
        self.assertNotContains(resp, 'Julkaise idea')

    def test_moderation_reason_shown_on_idea_page(self):
        idea = IdeaFactory()
        moderator = UserFactory()
        ModerationReason.objects.create(content_object=idea,
                                        moderator=moderator,
                                        reason='silly billy')
        resp = self.client.get('/fi/ideat/%d/' % idea.pk)
        self.assertContains(resp, 'moderoi sisältöä: silly billy')


class IdeaDetailFragmentTest(TestCase):
    def setUp(self):
        self.idea = IdeaFactory(title="My Tiiitle", description="My Deeescription")

    def test_open_detail_title_fragment(self):
        resp = self.client.get('/fi/ideat/%d/nayta/otsikko/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed('content/idea_detail_title.html')
        self.assertContains(resp, '<h1 class="h2-style">My Tiiitle')
        self.assertNotContains(resp, "My Deeescription")
        self.assertNotContains(resp, "<form")

    def test_open_description_fragment(self):
        resp = self.client.get('/fi/ideat/%d/nayta/kuvaus/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed('content/idea_detail_description.html')
        self.assertNotContains(resp, 'My Tiiitle')
        self.assertContains(resp, "My Deeescription")
        self.assertNotContains(resp, "<form")

    def test_open_owners_fragment(self):
        # TODO: Add another owner. The page slices the first owner out on purpose.
        """
        resp = self.client.get('/fi/ideat/%d/nayta/omistajat/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '@%s' % self.idea.owners.first().username)
        self.assertNotContains(resp, 'My Tiiitle')
        """

    def test_open_tags_fragment(self):
        resp = self.client.get('/fi/ideat/%d/nayta/aiheet/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '#%s' % self.idea.tags.first().name)
        self.assertNotContains(resp, 'My Tiiitle')

    def test_open_organizations_fragment(self):
        resp = self.client.get('/fi/ideat/%d/nayta/organisaatiot/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp,
                            '%s</a></li>' % self.idea.target_organizations.first().name)
        self.assertNotContains(resp, 'My Tiiitle')


class IdeaMainPictureTest(TestCase):
    test_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'nuka', 'testdata', 'lolcat-sample.jpg')

    def setUp(self):
        self.idea = IdeaFactory()
        user = self.idea.owners.first()
        self.client.login(username=user.username,
                          password=DEFAULT_PASSWORD)

    def test_upload_main_pic(self):
        self.assertRaises(ValueError, lambda: self.idea.picture.file)
        resp = self.client.post('/fi/ideat/%d/muokkaa/kuva/' % self.idea.pk, {
            'picture': open(self.test_file, 'rb')
        })
        self.assertEqual(resp.status_code, 200)
        idea2 = Idea.objects.get(pk=self.idea.pk)
        self.assertTrue(idea2.picture.url.endswith('.jpg'))
        self.assertTrue(idea2.picture_main.url.endswith('.jpg'))
        self.assertTrue(idea2.picture_narrow.url.endswith('.jpg'))

    def test_open_edit_picture_fragment_no_existing_pic(self):
        resp = self.client.get('/fi/ideat/%d/muokkaa/kuva/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_edit_picture_form.html')
        self.assertContains(resp, "Valitse kuva")
        self.assertNotContains(resp, "Nykyinen kuva")
        self.assertNotContains(resp, '<img')
        self.assertNotContains(resp, "Poista kuva")

    def test_open_edit_picture_fragment_with_existing_pic(self):
        self.idea.picture.save('lolcat.jpg', File(open(self.test_file, 'rb')))
        resp = self.client.get('/fi/ideat/%d/muokkaa/kuva/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_edit_picture_form.html')
        self.assertContains(resp, "Valitse kuva")
        self.assertContains(resp, "Poista kuva")
        self.assertContains(resp, "Nykyinen kuva")
        self.assertContains(resp, '<img')
        self.assertContains(resp, self.idea.picture_main.url)

    def test_open_picture_fragment_no_existing_pic(self):
        resp = self.client.get('/fi/ideat/%d/nayta/kuva/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_detail_picture.html')
        self.assertNotContains(resp, '<img')

    def test_open_picture_fragment_with_existing_pic(self):
        self.idea.picture.save('lolcat.jpg', File(open(self.test_file, 'rb')))
        resp = self.client.get('/fi/ideat/%d/nayta/kuva/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_detail_picture.html')
        self.assertNotContains(resp, "no-picture-container-editable")
        self.assertContains(resp, '<img')
        self.assertContains(resp, self.idea.picture_main.url)

    def tearDown(self):
        idea = Idea.objects.get(pk=self.idea)
        idea.picture.delete()


class IdeaEditFragmentTest(TestCase):
    def setUp(self):
        self.idea = IdeaFactory(title="My Tiiitle", description="My Deeescription")
        u = self.idea.owners.first()
        self.client.login(username=u.username, password=DEFAULT_PASSWORD)

    def login_as_moderator(self):
        mod = UserFactory(groups=[Group.objects.get(name=GROUP_NAME_MODERATORS)])
        self.client.login(username=mod.username, password=DEFAULT_PASSWORD)
        self.moderator = mod

    def test_open_edit_title_fragment(self):
        resp = self.client.get('/fi/ideat/%d/muokkaa/otsikko/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_edit_base_form.html')
        self.assertContains(resp, 'value="My Tiiitle"')
        self.assertNotContains(resp, 'My Deeescription')

    def test_open_edit_description_fragment(self):
        resp = self.client.get('/fi/ideat/%d/muokkaa/kuvaus/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_edit_base_form.html')
        self.assertNotContains(resp, 'My Tiiitle')
        self.assertContains(resp, "<form")
        self.assertContains(resp, "My Deeescription")

    def test_open_edit_owners_fragment(self):
        resp = self.client.get('/fi/ideat/%d/muokkaa/omistajat/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_edit_base_form.html')
        self.assertContains(resp, "<form")
        self.assertContains(resp, '>@%s</option>' % self.idea.owners.first().username)
        self.assertNotContains(resp, 'My Tiiitle')

    def test_open_edit_organizations_fragment(self):
        resp = self.client.get('/fi/ideat/%d/muokkaa/organisaatiot/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_edit_base_form.html')
        self.assertContains(resp, "<form")
        self.assertContains(resp, '>%s</option>' %
                            self.idea.target_organizations.first().name)
        self.assertNotContains(resp, 'My Tiiitle')

    def test_open_edit_tags_fragment(self):
        resp = self.client.get('/fi/ideat/%d/muokkaa/aiheet/' % self.idea.pk)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_edit_base_form.html')
        self.assertContains(resp, "<form")
        self.assertContains(resp, '<select')
        self.assertContains(resp, '#%s</option>' % self.idea.tags.first().name)
        self.assertNotContains(resp, 'My Tiiitle')

    def test_save_title_fragment(self):
        resp = self.client.post('/fi/ideat/%d/muokkaa/otsikko/' % self.idea.pk, {
            'title-fi': 'New Title'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue(resp['success'])
        self.assertEqual(resp['next'], '/fi/ideat/%d/nayta/otsikko/' % self.idea.pk)
        self.assertEqual('%s' % Idea.objects.get(pk=self.idea.pk).title, 'New Title')

    def test_save_description_fragment(self):
        resp = self.client.post('/fi/ideat/%d/muokkaa/kuvaus/' % self.idea.pk, {
            'description-fi': 'New Description',
            'upload_ticket': get_upload_signature()
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue(resp['success'])
        self.assertEqual(resp['next'], '/fi/ideat/%d/nayta/kuvaus/' % self.idea.pk)
        self.assertEqual('%s' % Idea.objects.get(pk=self.idea.pk).description,
                         'New Description')

    # no reason needed NK-415 (reverted)
    # def test_save_description_fragment_as_moderator_no_reason(self):
    #     self.login_as_moderator()
    #     resp = self.client.post('/fi/ideat/%d/muokkaa/kuvaus/' % self.idea.pk, {
    #         'description-fi': 'New Description',
    #         'upload_ticket': get_upload_signature()
    #     })
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertNotContains(resp, "Tämä kenttä vaaditaan.")

    def test_save_owners_fragment_as_moderator_reason_given(self):
        self.login_as_moderator()
        self.assertEqual(ModerationReason.objects.count(), 0)
        resp = self.client.post('/fi/ideat/%d/muokkaa/omistajat/' % self.idea.pk, {
            'owners': [self.idea.owners.first().pk, self.moderator.pk],
            '_moderation_reason': 'Added moderator as owner'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue(resp['success'])
        self.assertEqual(resp['next'], '/fi/ideat/%d/nayta/omistajat/' % self.idea.pk)
        self.assertEqual(Idea.objects.get(pk=self.idea.pk).owners.count(), 2)
        self.assertEqual(ModerationReason.objects.count(), 1)
        self.assertEqual(ModerationReason.objects.first().reason,
                         'Added moderator as owner')

    def test_save_owners_fragment(self):
        resp = self.client.post('/fi/ideat/%d/muokkaa/omistajat/' % self.idea.pk, {
            'owners': [self.idea.owners.first().pk, UserFactory().pk]
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue(resp['success'])
        self.assertEqual(resp['next'], '/fi/ideat/%d/nayta/omistajat/' % self.idea.pk)
        self.assertEqual(Idea.objects.get(pk=self.idea.pk).owners.count(), 2)

    def test_save_organizations_fragment(self):
        resp = self.client.post('/fi/ideat/%d/muokkaa/organisaatiot/' % self.idea.pk, {
            'target_organizations': [self.idea.target_organizations.first().pk,
                                     OrganizationFactory().pk]
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue(resp['success'])
        self.assertEqual(resp['next'], '/fi/ideat/%d/nayta/organisaatiot/' % self.idea.pk)
        self.assertEqual(Idea.objects.get(pk=self.idea.pk).target_organizations.count(),
                         2)

    def test_save_tags_fragment(self):
        self.assertEqual(self.idea.tags.count(), 1)
        resp = self.client.post('/fi/ideat/%d/muokkaa/aiheet/' % self.idea.pk, {
            'tags': [self.idea.tags.first().pk, TagFactory().pk]
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertTrue(resp['success'])
        self.assertEqual(resp['next'], '/fi/ideat/%d/nayta/aiheet/' % self.idea.pk)
        self.assertEqual(self.idea.tags.count(), 2)


class IdeaDescriptionSanitizationTest(TestCase):
    def test_cleaning(self):
        html = '<p><a href="#"><img src="hello.jpg" oncLick="window.close()"></a>' \
               '<script>alert(1)</script></p>'
        form = EditInitiativeDescriptionForm({'description-fi': html,
                                              'upload_ticket': get_upload_signature()})
        self.assertTrue(form.is_valid())
        desc = form.cleaned_data['description']
        self.assertEqual(desc,
                         {'fi': '<p><a href="#"><img src="hello.jpg"></a>alert(1)</p>'})


class InitiativeListTest(TestCase):
    def test_open_list(self):
        IdeaFactory(title="My UnPublished Idea",
                    status=Idea.STATUS_DRAFT,
                    visibility=Idea.VISIBILITY_DRAFT)
        IdeaFactory(title="My Published Idea",
                    status=Idea.STATUS_PUBLISHED,
                    visibility=Idea.VISIBILITY_PUBLIC)
        resp = self.client.get('/fi/selaa/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/initiative_list.html')
        self.assertContains(resp, 'My Published Idea')
        self.assertNotContains(resp, 'My UnPublished Idea')


class AdditionalDetailsTest(TestCase):

    def setUp(self):
        self.idea = IdeaFactory(title="My Tiiitle", description="My Deeescription")
        u = self.idea.owners.first()
        self.client.login(username=u.username, password=DEFAULT_PASSWORD)

    def test_visibility(self):
        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertNotContains(resp, '<section id="additional-details')

        CustomCommentFactory(
            content_type=ContentType.objects.get_for_model(self.idea),
            object_pk=self.idea.pk,
        )

        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertContains(resp, '<section id="additional-details')

    def test_visibility_as_draft(self):
        self.idea.status = Idea.STATUS_DRAFT
        self.idea.save()

        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertNotContains(resp, '<section id="additional-details')

    def test_add_detail(self):
        CustomCommentFactory(
            content_type=ContentType.objects.get_for_model(self.idea),
            object_pk=self.idea.pk,
        )
        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertContains(
            resp,
            '<a href="/fi/ideat/{}/uusi-lisatieto/"'.format(self.idea.pk)
        )

        added_detail = AdditionalDetailFactory(idea=self.idea)
        added_detail_cmp = AdditionalDetail.objects.first()

        self.assertEqual(self.idea.pk, added_detail_cmp.idea.pk)
        self.assertEqual(added_detail, added_detail_cmp)


class CreateQuestionTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.org = OrganizationFactory()

    def login(self):
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)

    def test_open_create_form(self):
        self.login()
        resp = self.client.get('/fi/kysymykset/uusi/{}/'.format(self.org.pk))
        self.assertContains(resp, '<h1>Kysy organisaatiolta', status_code=200)
        self.assertNotContains(resp, '>Tarkistuskoodi</label>', status_code=200)

    def test_create_form_anon(self):
        resp = self.client.get('/fi/kysymykset/uusi/{}/'.format(self.org.pk))
        self.assertContains(resp, '<h1>Kysy organisaatiolta', status_code=200)
        self.assertContains(resp, '>Tarkistuskoodi</label>', status_code=200)
        self.assertContains(resp, '>Lähettäjän nimi</label>', status_code=200)

    def test_create(self):
        self.login()
        self.assertEqual(Initiative.objects.count(), 0)
        resp = self.client.post('/fi/kysymykset/uusi/{}/'.format(self.org.pk), {
            'title': 'Why, oh why?',
            'description': 'My, oh my.',
            'target_organizations': [self.org.pk, ],
            'owners': [self.user.pk, ],
            'upload_ticket': get_upload_signature()
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Initiative.objects.count(), 1)
        self.assertEqual(Question._default_manager.count(), 1)
        self.assertEqual(Question.objects.count(), 1)
        obj = Initiative.objects.first()
        self.assertRedirects(resp, '/fi/kysymykset/%d/' % obj.pk)
        self.assertEqual(obj.creator, self.user)
        self.assertEqual(obj.target_organizations.count(), 1)
        self.assertEqual(obj.tags.count(), 0)
        self.assertEqual(obj.owners.count(), 1)


class QuestionEditAndPermTest(TestCase):

    def login(self, moderator=False):
        self.user = UserFactory()

        if moderator:
            self.user.groups.add(Group.objects.get(name=GROUP_NAME_MODERATORS))

        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)

    def test_edit_question(self):
        self.login()
        question = QuestionFactory()
        resp = self.client.get('/fi/ideat/{}/muokkaa/otsikko/'.format(question.pk))
        self.assertEqual(resp.status_code, 302)

    def test_edit_question_moderator(self):
        self.login(True)
        question = QuestionFactory()
        resp = self.client.get('/fi/ideat/{}/muokkaa/otsikko/'.format(question.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<form action="/fi/ideat/')
        resp = self.client.get('/fi/ideat/{}/muokkaa/omistajat/'.format(question.pk))
        self.assertEqual(resp.status_code, 200)

    def test_delete_question(self):
        self.login()
        question = QuestionFactory()
        resp = self.client.post('/fi/kysymys/{}/poista/'.format(question.pk))
        self.assertEqual(resp.status_code, 302)
        self.login(True)
        resp = self.client.post('/fi/kysymys/{}/poista/'.format(question.pk))
        self.assertEqual(resp.status_code, 200)

    def test_convert_to_idea(self):
        self.login(False)
        question = QuestionFactory(owners=[self.user.pk, ],)
        resp = self.client.post('/fi/ideat/muunna-kysymys-ideaksi/{}/'
                                .format(question.pk))
        self.assertEqual(resp.status_code, 200)
        # TODO: test user without right permission


@override_settings(CELERY_ALWAYS_EAGER=True)
class AttachmentUploadTest(TestCase):
    def setUp(self):
        self.upload_url = self.new_upload_url()

    def login(self):
        self.user = UserFactory()
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)

    def new_upload_url(self):
        return '/fi/liitteet/laheta/%s/' % get_upload_signature()

    def assert_upload_ok(self, resp, upload_count=None):
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertFalse('error' in data)
        self.assertTrue('filelink' in data)
        self.assertTrue('filename' in data)

        if upload_count is not None:
            self.assertEqual(Upload.objects.count(), upload_count)

    def assert_upload_failed(self, resp, error_message=None, upload_count=None):
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue('error' in data)
        self.assertFalse('filelink' in data)
        self.assertFalse('filename' in data)

        if error_message is not None:
            self.assertEqual(data['error'], error_message)

        if upload_count is not None:
            self.assertEqual(Upload.objects.count(), upload_count)

    def tearDown(self):
        Upload.objects.all().delete()


class AnonymousAttachmentUploadTest(AttachmentUploadTest):

    def test_upload_attachment_not_logged_in(self):
        resp = self.client.post(self.upload_url, {
            'file': ContentFile('123', 'hi.txt')
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Upload.objects.count(), 0)


def attachment_settings(**kwargs):
    opts = settings.ATTACHMENTS.copy()
    opts.update(kwargs)
    return {'ATTACHMENTS': opts}


class LoggedInAttachmentUploadTest(AnonymousAttachmentUploadTest):
    def test_upload_ok(self):
        self.login()
        resp = self.client.post(self.upload_url, {
            'file': ContentFile('123', 'hi.txt')
        })
        self.assert_upload_ok(resp, upload_count=1)
        self.assertEqual(UploadGroup.objects.count(), 1)

    @override_settings(**attachment_settings(max_size=2))
    def test_single_file_size_limit(self):
        self.login()
        resp1 = self.client.post(self.upload_url, {
            'file': ContentFile('12', 'hi.txt')
        })
        self.assert_upload_ok(resp1)
        resp2 = self.client.post(self.upload_url, {
            'file': ContentFile('123', 'hi.txt')
        })
        self.assert_upload_failed(resp2, upload_count=1,
                                  error_message="Tiedosto ylittää kokorajoituksen.")

    @override_settings(**attachment_settings(max_attachments_per_object=2))
    def test_too_many_files_per_object(self):
        self.login()
        resp1 = self.client.post(self.upload_url, {
            'file': ContentFile('123', 'hi.txt')
        })
        self.assert_upload_ok(resp1)
        resp2 = self.client.post(self.upload_url, {
            'file': ContentFile('123', 'hi.txt')
        })
        self.assert_upload_ok(resp2)
        resp3 = self.client.post(self.upload_url, {
            'file': ContentFile('123', 'hi.txt')
        })
        self.assert_upload_failed(resp3, upload_count=2,
                                  error_message="Liian monta liitetiedostoa lisätty.")

        # We should still be able to attach files to another object.
        resp4 = self.client.post(self.new_upload_url(), {
            'file': ContentFile('123', 'hi.txt')
        })
        self.assert_upload_ok(resp4)

    @override_settings(**attachment_settings(max_size_per_uploader=4))
    def test_uploader_size_limit(self):
        self.login()
        resp1 = self.client.post(self.upload_url, {
            'file': ContentFile('12', 'hi.txt')
        })
        self.assert_upload_ok(resp1)
        resp2 = self.client.post(self.new_upload_url(), {
            'file': ContentFile('123', 'hi.txt')
        })
        self.assert_upload_failed(
            resp2, upload_count=1,
            error_message="Olet lisännyt liian monta liitetiedostoa. "
                          "Yritä myöhemmin uudestaan."
        )

        # We should still be able to upload as another user.
        user2 = UserFactory()
        self.client.login(username=user2.username, password=DEFAULT_PASSWORD)
        resp1 = self.client.post(self.new_upload_url(), {
            'file': ContentFile('1234', 'hi.txt')
        })

    def test_unallowed_extension(self):
        self.login()
        resp1 = self.client.post(self.upload_url, {
            'file': ContentFile('12', 'hi.exe')
        })
        self.assert_upload_failed(resp1, upload_count=0,
                                  error_message="Tiedostotyyppi ei ole sallittu.")

    def test_allowed_extension_uppercase(self):
        self.login()
        resp1 = self.client.post(self.upload_url, {
            'file': ContentFile('12', 'hi.TXT')
        })
        self.assert_upload_ok(resp1)


class WarnUnpublishedIdeaTest(TestCase):
    def setUp(self):
        self.archive_date = date.today() - timedelta(days=30)
        self.warn_date = date.today() - timedelta(days=7)

    def test_exact_date(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT, created=self.warn_date)
        owner = idea.owners.first()
        warn_unpublished(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], owner.settings.email)
        self.assertEqual(
            mail.outbox[0].subject,
            "Idea '{}' on ollut julkaisematon 7 päivää.".format(idea.title)
        )
        msg = "Nuortenideat.fi idea '{}' on ollut luonnoksena 7 päivää ja " \
              "arkistoidaan 23 päivän kuluttua, jos sitä ei tähän mennessä julkaista."
        self.assertIn(msg.format(idea.title), mail.outbox[0].body)
        self.assertFalse('{%' in mail.outbox[0].body)

    def test_older_date(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, created=self.warn_date - timedelta(days=1))
        warn_unpublished(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_newer_date(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, created=self.warn_date + timedelta(days=1))
        warn_unpublished(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_organization_initiated_idea(self):
        organization = OrganizationFactory()
        admin = organization.admins.first()
        IdeaFactory(status=Idea.STATUS_DRAFT, initiator_organization=organization,
                    created=self.warn_date)
        warn_unpublished(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], admin.settings.email)

    def test_exact_date_with_status_published(self):
        IdeaFactory(created=self.warn_date)
        warn_unpublished(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_exact_date_with_visibility_archived(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, visibility=Idea.VISIBILITY_ARCHIVED,
                    created=self.warn_date)
        warn_unpublished(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_task_exact_date(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, created=self.warn_date)
        warn_unpublished_task()
        self.assertEqual(len(mail.outbox), 1)

    def test_task_older_date(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, created=self.warn_date - timedelta(days=1))
        warn_unpublished_task()
        self.assertEqual(len(mail.outbox), 0)

    def test_task_newer_date(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, created=self.warn_date + timedelta(days=1))
        warn_unpublished_task()
        self.assertEqual(len(mail.outbox), 0)


class ArchiveUnpublishedIdeaTest(TestCase):
    def setUp(self):
        self.archive_date = date.today() - timedelta(days=30)

    def test_exact_date(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT, created=self.archive_date)
        owner = idea.owners.first()
        archive_unpublished(self.archive_date)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_ARCHIVED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], owner.settings.email)
        self.assertEqual(
            mail.outbox[0].subject,
            "Idea '{}' on arkistoitu.".format(idea.title)
        )
        msg = "Nuortenideat.fi idea '{}' on ollut luonnos 30 päivää ja " \
              "on nyt automaattisesti arkistoitu.".format(idea.title)
        self.assertIn(msg, mail.outbox[0].body)
        self.assertFalse('{%' in mail.outbox[0].body)

    def test_older_date(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           created=self.archive_date - timedelta(days=1))
        archive_unpublished(self.archive_date)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_ARCHIVED)
        self.assertEqual(len(mail.outbox), 1)

    def test_newer_date(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           created=self.archive_date + timedelta(days=1))
        archive_unpublished(self.archive_date)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_PUBLIC)
        self.assertEqual(len(mail.outbox), 0)

    def test_organization_initiated_idea(self):
        organization = OrganizationFactory()
        admin = organization.admins.first()
        IdeaFactory(status=Idea.STATUS_DRAFT, initiator_organization=organization,
                    created=self.archive_date)
        archive_unpublished(self.archive_date)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], admin.settings.email)

    def test_exact_date_with_status_public(self):
        idea = IdeaFactory(status=Idea.STATUS_PUBLISHED,
                           created=self.archive_date)
        archive_unpublished(self.archive_date)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_PUBLIC)
        self.assertEqual(len(mail.outbox), 0)

    def test_exact_date_with_visibility_archived(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, visibility=Idea.VISIBILITY_ARCHIVED,
                    created=self.archive_date)
        archive_unpublished(self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_task_exact_date(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT, created=self.archive_date)
        archive_unpublished_task()
        self.assertEqual(len(mail.outbox), 1)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, Idea.VISIBILITY_ARCHIVED)

    def test_task_older_date(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           created=self.archive_date - timedelta(days=1))
        archive_unpublished_task()
        self.assertEqual(len(mail.outbox), 1)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, Idea.VISIBILITY_ARCHIVED)

    def test_task_newer_date(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           created=self.archive_date + timedelta(days=1))
        archive_unpublished_task()
        self.assertEqual(len(mail.outbox), 0)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, Idea.VISIBILITY_PUBLIC)


class RemindUntransferredIdeaTest(TestCase):
    def setUp(self):
        self.remind_date = date.today() - timedelta(30)
        self.archive_date = date.today() - timedelta(90)

    def test_exact_date(self):
        idea = IdeaFactory(published=self.remind_date)
        remind_untransferred(self.remind_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 2)

        for sent_mail in mail.outbox:
            self.assertEqual(
                sent_mail.subject,
                "Muistutus idean '{}' viemisestä eteenpäin.".format(idea.title)
            )
            msg = "Nuortenideat.fi idea '{}' on ollut julkaistuna 30 päivää ja " \
                  "arkistoidaan 60 päivän kuluttua, jos ideaa ei ole tähän mennessä " \
                  "viety eteenpäin.".format(idea.title)
            self.assertIn(msg, sent_mail.body)
            self.assertFalse('{%' in sent_mail.body)

        owner = idea.owners.first()
        contact_person = idea.target_organizations.first().admins.first()
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(len(mail.outbox[1].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], owner.settings.email)
        self.assertEqual(mail.outbox[1].recipients()[0], contact_person.settings.email)

    def test_older_date(self):
        IdeaFactory(published=self.remind_date - timedelta(days=1))
        remind_untransferred(self.remind_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_newer_date(self):
        IdeaFactory(published=self.remind_date + timedelta(days=1))
        remind_untransferred(self.remind_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_organization_initiated_idea(self):
        organization = OrganizationFactory()
        admin = organization.admins.first()
        idea = IdeaFactory(initiator_organization=organization,
                           published=self.remind_date)
        contact_person = idea.target_organizations.first().admins.first()
        self.assertEqual(len(mail.outbox), 0)
        remind_untransferred(self.remind_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(len(mail.outbox[1].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], admin.settings.email)
        self.assertEqual(mail.outbox[1].recipients()[0], contact_person.settings.email)

    def test_exact_date_with_status_draft(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, published=self.remind_date)
        remind_untransferred(self.remind_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_exact_date_with_visibility_archived(self):
        IdeaFactory(visibility=Idea.VISIBILITY_ARCHIVED, published=self.remind_date)
        remind_untransferred(self.remind_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_task_exact_date(self):
        IdeaFactory(published=self.remind_date)
        remind_untransferred_task()
        self.assertEqual(len(mail.outbox), 2)

    def test_task_older_date(self):
        IdeaFactory(published=self.remind_date - timedelta(days=1))
        remind_untransferred_task()
        self.assertEqual(len(mail.outbox), 0)

    def test_task_newer_date(self):
        IdeaFactory(published=self.remind_date + timedelta(days=1))
        remind_untransferred_task()
        self.assertEqual(len(mail.outbox), 0)


class WarnUntransferredIdeaTest(TestCase):
    def setUp(self):
        self.warn_date = date.today() - timedelta(60)
        self.archive_date = date.today() - timedelta(90)

    def test_exact_date(self):
        idea = IdeaFactory(published=self.warn_date)
        warn_untransferred(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 2)

        for sent_mail in mail.outbox:
            self.assertEqual(
                sent_mail.subject,
                "Muistutus idean '{}' viemisestä eteenpäin.".format(idea.title)
            )
            msg = "Nuortenideat.fi idea '{}' on ollut julkaistuna 60 päivää ja " \
                  "arkistoidaan 30 päivän kuluttua, jos ideaa ei ole tähän mennessä " \
                  "viety eteenpäin."
            self.assertIn(msg.format(idea.title), sent_mail.body)
            self.assertFalse('{%' in sent_mail.body)

        owner = idea.owners.first()
        contact_person = idea.target_organizations.first().admins.first()
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(len(mail.outbox[1].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], owner.settings.email)
        self.assertEqual(mail.outbox[1].recipients()[0], contact_person.settings.email)

    def test_older_date(self):
        IdeaFactory(published=self.warn_date - timedelta(days=1))
        warn_untransferred(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_newer_date(self):
        IdeaFactory(published=self.warn_date + timedelta(days=1))
        warn_untransferred(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_organization_initiated_idea(self):
        organization = OrganizationFactory()
        admin = organization.admins.first()
        idea = IdeaFactory(initiator_organization=organization, published=self.warn_date)
        contact_person = idea.target_organizations.first().admins.first()
        warn_untransferred(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(len(mail.outbox[1].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], admin.settings.email)
        self.assertEqual(mail.outbox[1].recipients()[0], contact_person.settings.email)

    def test_exact_date_with_status_draft(self):
        IdeaFactory(status=Idea.STATUS_DRAFT, published=self.warn_date)
        warn_untransferred(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_exact_date_with_visibility_archived(self):
        IdeaFactory(visibility=Idea.VISIBILITY_ARCHIVED,
                    published=self.archive_date - timedelta(days=1))
        warn_untransferred(self.warn_date, self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_task_exact_date(self):
        IdeaFactory(published=self.warn_date)
        warn_untransferred_task()
        self.assertEqual(len(mail.outbox), 2)

    def test_task_older_date(self):
        IdeaFactory(published=self.warn_date - timedelta(days=1))
        warn_untransferred_task()
        self.assertEqual(len(mail.outbox), 0)

    def test_task_newer_date(self):
        IdeaFactory(published=self.warn_date + timedelta(days=1))
        warn_untransferred_task()
        self.assertEqual(len(mail.outbox), 0)


class ArchiveUntransferredIdeaTest(TestCase):
    def setUp(self):
        self.archive_date = date.today() - timedelta(days=90)

    def test_exact_date(self):
        idea = IdeaFactory(status=Idea.STATUS_PUBLISHED, published=self.archive_date)
        archive_untransferred(self.archive_date)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_ARCHIVED)

        self.assertEqual(len(mail.outbox), 2)
        for new_mail in mail.outbox:
            self.assertEqual(new_mail.subject,
                             "Idea '{}' on arkistoitu.".format(idea.title))
            msg = "Nuortenideat.fi idea '{}' on ollut julkaistuna 90 päivää ja " \
                "automaattisesti arkistoitiin, koska ideaa ei oltu viety eteenpäin." \
                .format(idea.title)
            self.assertIn(msg, new_mail.body)
            self.assertFalse('{%' in new_mail.body)

        owner = idea.owners.first()
        contact_person = idea.target_organizations.first().admins.first()
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(len(mail.outbox[1].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], owner.settings.email)
        self.assertEqual(mail.outbox[1].recipients()[0], contact_person.settings.email)

    def test_older_date(self):
        idea = IdeaFactory(status=Idea.STATUS_PUBLISHED,
                           published=self.archive_date - timedelta(days=1))
        archive_untransferred(self.archive_date)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_ARCHIVED)
        self.assertEqual(len(mail.outbox), 2)

    def test_newer_date(self):
        idea = IdeaFactory(status=Idea.STATUS_PUBLISHED,
                           published=self.archive_date + timedelta(days=1))
        archive_untransferred(self.archive_date)
        idea = Idea.objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_PUBLIC)
        self.assertEqual(len(mail.outbox), 0)

    def test_exact_date_with_status_draft(self):
        idea = IdeaFactory(status=Idea.STATUS_DRAFT,
                           published=self.archive_date - timedelta(days=1))
        archive_untransferred(self.archive_date)
        idea = Idea.objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_PUBLIC)
        self.assertEqual(len(mail.outbox), 0)

    def test_exact_date_with_visibility_archived(self):
        IdeaFactory(visibility=Idea.VISIBILITY_ARCHIVED,
                    published=self.archive_date - timedelta(days=1))
        archive_untransferred(self.archive_date)
        self.assertEqual(len(mail.outbox), 0)

    def test_organization_initiated_idea(self):
        organization = OrganizationFactory()
        admin = organization.admins.first()
        idea = IdeaFactory(initiator_organization=organization,
                           published=self.archive_date)
        contact_person = idea.target_organizations.first().admins.first()
        archive_untransferred(self.archive_date)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, idea.VISIBILITY_ARCHIVED)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(len(mail.outbox[0].recipients()), 1)
        self.assertEqual(len(mail.outbox[1].recipients()), 1)
        self.assertEqual(mail.outbox[0].recipients()[0], admin.settings.email)
        self.assertEqual(mail.outbox[1].recipients()[0], contact_person.settings.email)

    def test_task_exact_date(self):
        idea = IdeaFactory(published=self.archive_date)
        archive_untransferred_task()
        self.assertEqual(len(mail.outbox), 2)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, Idea.VISIBILITY_ARCHIVED)

    def test_task_older_date(self):
        idea = IdeaFactory(published=self.archive_date - timedelta(days=1))
        archive_untransferred_task()
        self.assertEqual(len(mail.outbox), 2)
        idea = Idea.unmoderated_objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, Idea.VISIBILITY_ARCHIVED)

    def test_task_newer_date(self):
        idea = IdeaFactory(published=self.archive_date + timedelta(days=1))
        archive_untransferred_task()
        self.assertEqual(len(mail.outbox), 0)
        idea = Idea.objects.get(pk=idea.pk)
        self.assertEqual(idea.visibility, Idea.VISIBILITY_PUBLIC)


@skipUnless(settings.CLAMAV['enabled'], "ClamAV disabled")
class VirusUploadTest(AttachmentUploadTest):
    def test_virus_detected(self):
        self.login()
        resp = self.client.post(self.upload_url, {
            'file': ContentFile('X5O!P%@AP[4\PZX54(P^)7CC)7}'
                                '$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*', 'evil.txt')
        })
        self.assert_upload_failed(resp, upload_count=0,
                                  error_message="Tiedosto ei läpäissyt virustarkistusta. "
                                  "Löytynyt virus: Eicar-Test-Signature")

    def test_no_virus_detected(self):
        self.login()
        resp = self.client.post(self.upload_url, {
            'file': ContentFile('X5O!P%@AP[4\PZX54(P^)7CC)7}'
                                '$EIGAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*', 'evil.txt')
        })                        # ^ typo /s/C/G/ -> so it's obviously not a virus
        self.assert_upload_ok(resp)


class IdeaPdfTest(TestCase):
    def setUp(self):
        # login
        self.user = UserFactory()
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)

        # create idea
        self.idea = IdeaFactory(
            creator=self.user,
            status=Idea.STATUS_PUBLISHED,
            visibility=Idea.VISIBILITY_DRAFT,
        )

        # add comments
        CustomCommentFactory(
            content_type=ContentType.objects.get_for_model(self.idea),
            object_pk=self.idea.pk
        )

    def test_permission(self):
        # logout
        self.client.logout()
        # try open pdf view
        resp = self.client.get('/fi/ideat/{}/pdf-luonti/'.format(self.idea.pk))
        self.assertEqual(resp.status_code, 302)

    def test_not_published(self):
        self.idea.status = Idea.STATUS_TRANSFERRED
        self.idea.save()
        resp = self.client.get('/fi/ideat/{}/pdf-luonti/'.format(self.idea.pk))
        self.assertEqual(resp.status_code, 302)

    def test_pdf_content(self):
        # open pdf view
        resp = self.client.get('/fi/ideat/{}/pdf-luonti/'.format(self.idea.pk))
        self.assertEqual(resp.status_code, 200)
        # check necessary elements
        self.assertContains(resp, 'Tämä on PDF-luonnin esikatselu. Voit vielä piilottaa '
                                  'kommentteja ennen tulostusta.')
        self.assertContains(resp, '<h3 class="h4-style">Kommentit (1)</h3>')
        self.assertContains(resp, '<select multiple="multiple" class="form-control" '
                                  'id="id_included_comments"')
        self.assertContains(resp, '<input', 13)


class IdeaSearchFormTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)

    def test_status_label_counts(self):
        IdeaFactory.create_batch(4, status=Idea.STATUS_PUBLISHED)
        IdeaFactory.create_batch(3, status=Idea.STATUS_TRANSFERRED)
        IdeaFactory.create_batch(2, status=Idea.STATUS_DECISION_GIVEN)
        IdeaFactory(status=Idea.STATUS_PUBLISHED, visibility=Idea.VISIBILITY_ARCHIVED,
                    owners=[self.user])

        form = IdeaSearchForm(**{'user': self.user})
        choices = dict(form.fields["status"].choices)
        self.assertTrue("" in choices)
        self.assertEqual(choices[""], "Kaikki (9)")

        self.assertTrue(Idea.STATUS_PUBLISHED in choices)
        self.assertEqual(choices[Idea.STATUS_PUBLISHED], "Avoin (4)")

        self.assertTrue(Idea.STATUS_TRANSFERRED in choices)
        self.assertEqual(choices[Idea.STATUS_TRANSFERRED], "Viety eteenpäin (3)")

        self.assertTrue(Idea.STATUS_DECISION_GIVEN in choices)
        self.assertEqual(choices[Idea.STATUS_DECISION_GIVEN], "Päätös annettu (2)")

        self.assertTrue(Idea.VISIBILITY_ARCHIVED in choices)
        self.assertEqual(choices[Idea.VISIBILITY_ARCHIVED], "Arkistoitu (1)")


class IdeaFavoriteTest(TestCase):

    def setUp(self):
        # login
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)

        # create idea
        self.idea = IdeaFactory(
            creator=self.user2,
            status=Idea.STATUS_PUBLISHED,
            visibility=Idea.VISIBILITY_DRAFT,
        )

    def test_follow_idea(self):
        ct = ContentType.objects.get_for_model(Idea)
        resp = self.client.post('/fi/suosikit/seuraa/{}/{}/'.format(ct.pk, self.idea.pk))
        self.assertEqual(resp.status_code, 200)

