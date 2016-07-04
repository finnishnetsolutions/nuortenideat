# coding=utf-8

from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from account.factories import UserFactory, DEFAULT_PASSWORD
from content.factories import IdeaFactory
from content.models import Idea
from nuka.test.testcases import TestCase

from .factories import CustomCommentFactory
from .models import CustomComment


"""
# TODO: Login works, FIXME.
class DeleteTest(TestCase):
    def setUp(self):
        self.idea = IdeaFactory()
        self.idea_content_type = ContentType.objects.get_for_model(Idea)
        self.group_admin = Group.objects.get(name=GROUP_NAME_ADMINS)
        self.group_moderator = Group.objects.get(name=GROUP_NAME_MODERATORS)
        self.user = UserFactory(settings__first_name="Matti",
                                settings__last_name="Meikäläinen")

    def test_own(self):
        self.user.groups.clear()
        self.user.groups.add(self.group_moderator)
        login = self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        self.assertNotEqual(login, False)

        comment = CustomComment.objects.create(
            content_type=self.idea_content_type,
            object_pk=self.idea.pk,
            user=self.user,
            comment="Some comment text",
            site_id=1
        )

        resp = self.client.post("/fi/ideat/poista_kommentti/{0}/".format(comment.pk),
                                follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "nkcomments/comment_list_item_deleted.html")
        self.assertContains(resp, "Kommentti poistettu.")
        self.assertNotContains(resp, comment.comment)
        with self.assertRaises(ObjectDoesNotExist):
            CustomComment.objects.get(pk=comment.pk)

    def test_as_moderator(self):
        pass

    def test_unauthorized(self):
        pass
"""


class WriteCommentTest(TestCase):

    def setUp(self):
        pass

    def manual_set_up(self, public=True, login=False):
        if public:
            status = Idea.STATUS_PUBLISHED
            visibility = Idea.VISIBILITY_PUBLIC
        else:
            status = Idea.STATUS_DRAFT
            visibility = Idea.VISIBILITY_DRAFT

        self.user = UserFactory()
        self.idea = IdeaFactory(
            creator=self.user,
            status=status,
            visibility=visibility,
        )

        if login:
            self.user = self.idea.creator
            self.client.login(username=self.user.username,
                              password=DEFAULT_PASSWORD)

    def test_comment_block_visibility_public_idea(self):
        self.manual_set_up()
        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_detail.html')
        self.assertContains(resp, '<article id="comments"')
        self.assertContains(resp, '<h4>Kommentit (0)</h4>')

    def test_comment_block_pvisibility_not_public_idea(self):
        self.manual_set_up(public=False, login=True)
        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'content/idea_detail.html')
        self.assertNotContains(resp, '<div class="well" id="comments">')

    def test_write_comment(self):

        self.manual_set_up(login=True)

        comment = CustomCommentFactory(
            content_type=ContentType.objects.get_for_model(self.idea),
            object_pk=self.idea.pk
        )
        comment_cmp = CustomComment.objects.first()
        self.assertIsNotNone(comment_cmp)
        self.assertEqual(comment_cmp, comment)

        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertContains(resp, comment.comment)

    def test_comment_block_necessary_elements(self):
        self.manual_set_up(login=True)
        CustomCommentFactory(
            content_type=ContentType.objects.get_for_model(self.idea),
            object_pk=self.idea.pk,
            user_id=self.user.pk
        )
        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertNotContains(resp, '<div id="id_name_wrap"')
        self.assertContains(resp, 'title="Poista kommentti"')

    def test_comment_block_necessary_elements_anonymous(self):
        self.manual_set_up()
        CustomCommentFactory(
            content_type=ContentType.objects.get_for_model(self.idea),
            object_pk=self.idea.pk,
        )
        resp = self.client.get('/fi/ideat/{}'.format(self.idea.pk), follow=True)
        self.assertNotContains(resp, '<input id="id_name" name="name" type="hidden">')
        self.assertContains(resp, '<div id="id_name_wrap"')
        self.assertContains(resp, '<div id="id_comment_wrap"')
        self.assertNotContains(resp, 'title="Poista kommentti"')
