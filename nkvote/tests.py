# coding=utf-8

from __future__ import unicode_literals

from uuid import uuid4

from django.contrib.auth.models import AnonymousUser, Group
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.test.client import RequestFactory

from account.factories import UserFactory, DEFAULT_PASSWORD
from account.models import GROUP_NAME_ADMINS, GROUP_NAME_MODERATORS
from content.factories import IdeaFactory
from content.models import Idea
from nkcomments.models import CustomComment
from nkvote.models import Answer
from nkvote.utils import get_client_identifier, answered_gallup, answered_options, vote
from nuka.test.testcases import TestCase as NukaTestCase

from .utils import get_voter, get_voted_objects, answered_gallups
from .models import Vote, Voter, Gallup, Question, Option


USER_AGENT = "test-agent"
REMOTE_ADDR = "127.0.0.1"
HEADERS = {"HTTP_USER_AGENT": USER_AGENT, "REMOTE_ADDR": REMOTE_ADDR}


class UtilsGetVoterTest(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.idea = IdeaFactory()
        self.user = UserFactory()

    def test_create_when_logged_in(self):
        """ Tests whether get_voter creates correctly new voter, when no old
            ones are present and we are logged in without cookies. """
        request = self.request_factory.get("/selaa/")
        request.user = self.user
        resp = get_voter(request)

        self.assertIsInstance(resp, Voter)
        self.assertEqual(resp.user, self.user)
        self.assertNotEqual(resp.voter_id, None)

    def test_create_when_logged_out(self):
        """ Tests whether get_voter creates correctly new voter, when no old
            ones are present and we are not logged in but have cookies set. """
        request = self.request_factory.get("/selaa/")
        request.user = AnonymousUser
        resp = get_voter(request)

        self.assertIsInstance(resp, Voter)
        self.assertEqual(resp.user, None)
        self.assertNotEqual(resp.voter_id, None)

    def test_return_when_logged_in(self):
        """ Tests whether get_voter returns correctly already existing voter
            when we try it while logged in. """
        voter_id = uuid4().hex
        voter = Voter.objects.create(user=self.user, voter_id=voter_id)

        request = self.request_factory.get("/selaa/")
        request.user = self.user
        resp = get_voter(request)

        self.assertIsInstance(resp, Voter)
        self.assertEqual(resp, voter)
        self.assertEqual(resp.user, self.user)
        self.assertEqual(resp.voter_id, voter_id)

    def test_return_when_logged_out(self):
        """ Tests whether get_voter returns correctly already existing voter
            when we try it while logged out. """
        voter_id = uuid4().hex
        voter = Voter.objects.create(user=None, voter_id=voter_id)

        request = self.request_factory.get("/selaa/")
        request.user = AnonymousUser
        request.COOKIES[Voter.VOTER_COOKIE] = voter_id
        resp = get_voter(request)

        self.assertIsInstance(resp, Voter)
        self.assertEqual(resp, voter)
        self.assertEqual(resp.user, None)
        self.assertEqual(resp.voter_id, voter_id)

    def test_return_with_cookies_logged_in(self):
        """ Tests whether get_voter returns correctly already existing voter
            when we try it while logged in and the voter_id cookie set. """
        voter_id = uuid4().hex
        voter = Voter.objects.create(user=self.user, voter_id=voter_id)

        request = self.request_factory.get("/selaa/")
        request.user = self.user
        resp = get_voter(request)

        self.assertIsInstance(resp, Voter)
        self.assertEqual(resp, voter)
        self.assertEqual(resp.user, self.user)
        self.assertEqual(resp.voter_id, voter_id)

    def test_return_with_cookies_logged_out(self):
        """ Tests whether get_voter returns correctly already existing voter
            when we try it while logged out and the voter_id cookie set. """
        # Seems to be exactly the same as test_return_when_logged_out.
        voter_id = uuid4().hex
        voter = Voter.objects.create(user=None, voter_id=voter_id)

        request = self.request_factory.get("/selaa/")
        request.user = AnonymousUser
        request.COOKIES[Voter.VOTER_COOKIE] = voter_id
        resp = get_voter(request)

        self.assertIsInstance(resp, Voter)
        self.assertEqual(resp, voter)
        self.assertEqual(resp.user, None)
        self.assertEqual(resp.voter_id, voter_id)


class UtilsGetVotedObjectsTest(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = UserFactory()
        self.ideas = (
            IdeaFactory(),
            IdeaFactory(),
        )
        idea_content_type = ContentType.objects.get_for_model(Idea)
        self.comments = (
            CustomComment.objects.create(
                content_type=idea_content_type,
                object_pk=self.ideas[0].pk,
                user_name="A Person",
                comment="Comment #1",
                site_id=1
            ),
            CustomComment.objects.create(
                content_type=idea_content_type,
                object_pk=self.ideas[1].pk,
                user_name="Someone",
                comment="Comment #2",
                site_id=1
            ),
        )

    def test_ideas(self):
        request = self.request_factory.post(
            "/fi/ideat/{}/kannata/".format(self.ideas[0].id), **HEADERS
        )
        request.user = AnonymousUser()

        vote_object = vote(request, Idea, self.ideas[0].pk, Vote.VOTE_UP)
        self.assertNotEqual(vote_object, False)

        request.COOKIES[Voter.VOTER_COOKIE] = vote_object.voter.voter_id
        voted_ids = get_voted_objects(request, [self.ideas[0], self.ideas[1]], Idea)

        # Expect only the voted idea 0 to be returned.
        self.assertListEqual(voted_ids, [self.ideas[0].id])

    def test_comments(self):
        request = self.request_factory.post(
            "/fi/kommentit/{}/kannata".format(self.comments[0].pk), **HEADERS
        )
        request.user = AnonymousUser()

        vote_object = vote(request, CustomComment, self.comments[0].pk, Vote.VOTE_UP)
        self.assertNotEqual(vote_object, False)

        request.COOKIES[Voter.VOTER_COOKIE] = vote_object.voter.voter_id
        voted_ids = get_voted_objects(request, self.comments, CustomComment)

        # Expect only the voted comment 0 to be returned.
        self.assertListEqual(voted_ids, [self.comments[0].pk])


class IdeasVoteTest(TestCase):
    # TODO: Test voting only possible on published, public ideas.

    def setUp(self):
        self.idea = IdeaFactory()

    def test_anonymous(self):
        # Check no votes are present.
        self.assertEqual(self.idea.votes.count(), 0)

        # Add a vote.
        resp = self.client.post(
            "/fi/ideat/{0}/kannata/".format(self.idea.id),
            follow=True, **HEADERS
        )
        self.assertEqual(resp.status_code, 200)

        # Assert that one vote is present.
        self.assertEqual(self.idea.votes.count(), 1)

    def test_logged_in(self):
        # Log in.
        user = UserFactory()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)

        # Check no votes are present and add a vote.
        self.assertEqual(self.idea.votes.count(), 0)
        resp = self.client.post(
            "/fi/ideat/{0}/kannata/".format(self.idea.id),
            follow=True, **HEADERS
        )
        self.assertEqual(resp.status_code, 200)

        # Assert that one vote is present.
        self.assertEqual(self.idea.votes.count(), 1)

    def test_anonymous_then_logged_in(self):
        """ Tests that you won't be able to vote first as anonymous and then again
            the same idea when logged in. """
        # Add a vote without logging in and assert it being added.
        self.assertEqual(self.idea.votes.count(), 0)
        resp = self.client.post(
            "/fi/ideat/{0}/kannata/".format(self.idea.id),
            follow=True, **HEADERS
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.idea.votes.count(), 1)

        # Log in.
        user = UserFactory()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)

        # Add another vote and assert it not being added.
        resp = self.client.post(
            "/fi/ideat/{0}/kannata/".format(self.idea.id),
            follow=True, **HEADERS
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.idea.votes.count(), 1)

    def test_vote_twice_the_same(self):
        # Test that there is no votes and add one vote.
        self.assertEqual(self.idea.votes.count(), 0)
        resp = self.client.post(
            "/fi/ideat/{0}/kannata/".format(self.idea.id),
            follow=True, **HEADERS
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.idea.votes.count(), 1)

        # Try to add another vote.
        resp = self.client.post(
            "/fi/ideat/{0}/kannata/".format(self.idea.id),
            follow=True, **HEADERS
        )
        self.assertEqual(resp.status_code, 200)

        # Still should be only 1 vote, since you can't vote twice.
        self.assertEqual(self.idea.votes.count(), 1)

    def test_support(self):
        resp = self.client.post(
            "/fi/ideat/{0}/kannata/".format(self.idea.id),
            follow=True, **HEADERS
        )
        self.assertEqual(resp.status_code, 200)

        votes = self.idea.votes
        self.assertEqual(votes.count(), 1)

        the_vote = self.idea.votes.first()
        self.assertEqual(the_vote.choice, Vote.VOTE_UP)
        self.assertEqual(the_vote.content_object, self.idea)

    def test_oppose(self):
        resp = self.client.post(
            "/fi/ideat/{0}/vastusta/".format(self.idea.id),
            follow=True, **HEADERS
        )
        self.assertEqual(resp.status_code, 200)

        votes = self.idea.votes
        self.assertEqual(votes.count(), 1)

        the_vote = self.idea.votes.first()
        self.assertEqual(the_vote.choice, Vote.VOTE_DOWN)
        self.assertEqual(the_vote.content_object, self.idea)


class CommentsVoteTest(TestCase):

    def setUp(self):
        self.idea = IdeaFactory()
        idea_content_type = ContentType.objects.get_for_model(Idea)
        self.comments = (
            CustomComment.objects.create(
                content_type=idea_content_type,
                object_pk=self.idea.pk,
                user_name="A Person",
                comment="Comment #1",
                site_id=1
            ),
            CustomComment.objects.create(
                content_type=idea_content_type,
                object_pk=self.idea.pk,
                user_name="Someone",
                comment="Comment #2",
                site_id=1
            ),
        )

    def test_support(self):
        resp = self.client.post(
            "/fi/kommentit/{0}/kannata/".format(self.comments[0].id),
            **HEADERS
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.comments[0].votes.count(), 1)

        the_vote = self.comments[0].votes.first()
        self.assertEqual(the_vote.choice, Vote.VOTE_UP)
        self.assertEqual(the_vote.content_object, self.comments[0])

    def test_oppose(self):
        resp = self.client.post(
            "/fi/kommentit/{0}/vastusta/".format(self.comments[0].id),
            **HEADERS
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.comments[0].votes.count(), 1)

        the_vote = self.comments[0].votes.first()
        self.assertEqual(the_vote.choice, Vote.VOTE_DOWN)
        self.assertEqual(the_vote.content_object, self.comments[0])


class GallupUtilsTest(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()
        self.idea = IdeaFactory()
        self.gallups = [
            Gallup.objects.create(idea=self.idea),
            Gallup.objects.create(idea=self.idea)
        ]
        self.questions = [
            Question.objects.create(text="Question #1", gallup=self.gallups[0]),
            Question.objects.create(text="Question #2", gallup=self.gallups[0]),
            Question.objects.create(text="Question #3", gallup=self.gallups[1]),
            Question.objects.create(text="Question #4", gallup=self.gallups[1])
        ]
        self.options = [
            Option.objects.create(text="Option #1", question=self.questions[0]),
            Option.objects.create(text="Option #2", question=self.questions[0]),
            Option.objects.create(text="Option #3", question=self.questions[1]),
            Option.objects.create(text="Option #4", question=self.questions[1]),
            Option.objects.create(text="Option #5", question=self.questions[2]),
            Option.objects.create(text="Option #6", question=self.questions[2]),
            Option.objects.create(text="Option #7", question=self.questions[3]),
            Option.objects.create(text="Option #8", question=self.questions[3])
        ]

    def test_setup(self):
        self.assertEqual(len(self.gallups), 2)
        for gallup in self.gallups:
            self.assertEqual(gallup.question_set.count(), 2)
            for question in gallup.question_set.all():
                self.assertEqual(question.option_set.count(), 2)

    def test_answered_gallups(self):
        request = self.request_factory.get("/ideat/{0}".format(self.idea.pk), **HEADERS)
        request.user = AnonymousUser()

        voter = get_voter(request)
        request.COOKIES[Voter.VOTER_COOKIE] = voter.voter_id

        Answer.objects.create(
            gallup=self.gallups[0],
            voter=voter,
            client_identifier=get_client_identifier(request)
        )
        result = answered_gallups(request)
        self.assertEqual(len(result), 1)
        self.assertListEqual(result, [self.gallups[0]])

    def test_answered_gallup(self):
        request = self.request_factory.get("/ideat/{0}".format(self.idea.pk), **HEADERS)
        request.user = AnonymousUser()

        voter = get_voter(request)
        request.COOKIES[Voter.VOTER_COOKIE] = voter.voter_id

        Answer.objects.create(
            gallup=self.gallups[0],
            voter=voter,
            client_identifier=get_client_identifier(request)
        )

        result = answered_gallup(request, self.gallups[0])
        self.assertEqual(result, True)

    def test_answered_options(self):
        request = self.request_factory.get("/ideat/{0}".format(self.idea.pk), **HEADERS)
        request.user = AnonymousUser()

        voter = get_voter(request)
        request.COOKIES[Voter.VOTER_COOKIE] = voter.voter_id

        answer = Answer.objects.create(
            gallup=self.gallups[0],
            voter=voter,
            client_identifier=get_client_identifier(request)
        )
        choices = [self.options[0], self.options[2]]
        answer.choices.add(*choices)
        result = answered_options(request)

        self.assertSetEqual(set(result), set(choices))


class GallupTest(NukaTestCase):
    # TODO: Tests for different languages.
    
    def setUp(self):
        self.request_factory = RequestFactory()
        self.idea = IdeaFactory()

    def setUp_gallups(self):
        self.gallups = [
            Gallup.objects.create(idea=self.idea),
            Gallup.objects.create(idea=self.idea)
        ]
        self.questions = [
            Question.objects.create(text="Question #1", gallup=self.gallups[0]),
            Question.objects.create(text="Question #2", gallup=self.gallups[0]),
            Question.objects.create(text="Question #3", gallup=self.gallups[1]),
            Question.objects.create(text="Question #4", gallup=self.gallups[1])
        ]
        self.options = [
            Option.objects.create(text="Option #1", question=self.questions[0]),
            Option.objects.create(text="Option #2", question=self.questions[0]),
            Option.objects.create(text="Option #3", question=self.questions[1]),
            Option.objects.create(text="Option #4", question=self.questions[1]),
            Option.objects.create(text="Option #5", question=self.questions[2]),
            Option.objects.create(text="Option #6", question=self.questions[2]),
            Option.objects.create(text="Option #7", question=self.questions[3]),
            Option.objects.create(text="Option #8", question=self.questions[3])
        ]

    def setUp_gallup(self):
        self.gallup = Gallup.objects.create(idea=self.idea)
        self.questions = [
            Question.objects.create(text="Question #1", gallup=self.gallup),
            Question.objects.create(text="Question #2", gallup=self.gallup)
        ]
        self.options = [
            Option.objects.create(text="Option #1", question=self.questions[0]),
            Option.objects.create(text="Option #2", question=self.questions[0]),
            Option.objects.create(text="Option #3", question=self.questions[1]),
            Option.objects.create(text="Option #4", question=self.questions[1])
        ]

    def test_get_results(self):
        self.setUp_gallups()
        self.gallups[0].status = Gallup.STATUS_OPEN
        self.gallups[0].save()
        url = "/fi/ideat/{0}/gallup/{1}/tulokset/"
        url = url.format(self.idea.pk, self.gallups[0].pk)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "gallup/well.html")
        self.assertContains(resp, "Question #1", 1)
        self.assertContains(resp, "Option #1", 1)
        self.assertContains(resp, "Option #2", 1)
        self.assertContains(resp, "Question #2", 1)
        self.assertContains(resp, "Option #3", 1)
        self.assertContains(resp, "Option #4", 1)
        self.assertContains(resp, "<div class=\"progress\">", 4)
        self.assertNotContains(resp, "Äänestä")
        self.assertEqual(self.gallups[0].answer_set.count(), 0)

    def test_answer_draft(self):
        self.setUp_gallup()
        url = "/fi/ideat/{0}/gallup/{1}/vastaa/".format(self.idea.pk, self.gallup.pk)
        resp = self.client.post(
            url,
            {
                "question-{0}_option".format(self.questions[0].pk): str(self.options[0].pk),
                "question-{0}_option".format(self.questions[1].pk): str(self.options[3].pk),
            },
            follow=True,
            **HEADERS
        )
        self.assertRedirects(resp, "/fi/kayttaja/kirjaudu-sisaan/?next={}".format(url))
        self.assertContains(resp, "Ei käyttöoikeutta.")
        self.assertEqual(self.gallup.answer_set.count(), 0)

    def test_answer_open(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_OPEN
        self.gallup.save()
        resp = self.client.post(
            "/fi/ideat/{0}/gallup/{1}/vastaa/".format(self.idea.pk, self.gallup.pk),
            {
                "question-{0}_option".format(self.questions[0].pk): str(self.options[0].pk),
                "question-{0}_option".format(self.questions[1].pk): str(self.options[3].pk),
            },
            **HEADERS
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "gallup/well.html")
        self.assertContains(resp, "Question #1", 1)
        self.assertContains(resp, "Option #1", 1)
        self.assertContains(resp, "Option #2", 1)
        self.assertContains(resp, "Question #2", 1)
        self.assertContains(resp, "Option #3", 1)
        self.assertContains(resp, "Option #4", 1)
        self.assertNotContains(resp, "Äänestä")
        self.assertEqual(self.gallup.answer_set.count(), 1)

    def test_answer_closed(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_CLOSED
        self.gallup.save()
        url = "/fi/ideat/{0}/gallup/{1}/vastaa/".format(self.idea.pk, self.gallup.pk)
        resp = self.client.post(
            url,
            {
                "question-{0}_option".format(self.questions[0].pk): str(self.options[0].pk),
                "question-{0}_option".format(self.questions[1].pk): str(self.options[3].pk),
            },
            follow=True,
            **HEADERS
        )
        self.assertRedirects(resp, "/fi/kayttaja/kirjaudu-sisaan/?next={}".format(url))
        self.assertContains(resp, "Ei käyttöoikeutta.")
        self.assertEqual(self.gallup.answer_set.count(), 0)

    def test_create_gallup(self):
        self.client.login(
            username=self.idea.owners.first().username,
            password=DEFAULT_PASSWORD
        )
        question_texts = ["Question #1", "Question #2"]
        option_texts = ["Option #1", "Option #2", "Option #3", "Option #4"]
        resp = self.client.post(
            "/fi/ideat/{0}/gallup/uusi/".format(self.idea.pk),
            {
                "q-1-fi": question_texts[0],
                "q-1_o-1-fi": option_texts[0],
                "q-1_o-2-fi": option_texts[1],
                "q-2-fi": question_texts[1],
                "q-2_o-1-fi": option_texts[2],
                "q-2_o-2-fi": option_texts[3],
                "default_view": "questions"
            },
            follow=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Kirjaudu sisään")
        self.assertContains(resp, "Gallup tallennettu.")
        self.assertContains(resp, question_texts[0])
        self.assertContains(resp, option_texts[0])
        self.assertContains(resp, option_texts[1])
        self.assertContains(resp, question_texts[1])
        self.assertContains(resp, option_texts[2])
        self.assertContains(resp, option_texts[3])
        self.assertTemplateUsed(resp, "content/idea_detail.html")

        self.assertEqual(self.idea.gallup_set.count(), 1)
        gallup = Gallup.objects.last()
        self.assertEqual(gallup.is_draft(), True)

        # Assert the questions were set correctly.
        questions = Question.objects.filter(gallup=gallup).order_by("text")
        result_question_texts = list(questions.values_list("text", flat=True))
        question_texts = ["{\"fi\": \""+text+"\"}" for text in question_texts]
        self.assertListEqual(question_texts, result_question_texts)

        # Assert the options were set correctly.
        options = Option.objects.filter(question__gallup=gallup).order_by("text")
        result_option_texts = list(options.values_list("text", flat=True))
        option_texts = ["{\"fi\": \""+text+"\"}" for text in option_texts]
        self.assertListEqual(result_option_texts, option_texts)

    def test_open_gallup(self):
        self.client.login(
            username=self.idea.owners.first().username,
            password=DEFAULT_PASSWORD
        )
        gallup = Gallup.objects.create(idea=self.idea, status=Gallup.STATUS_DRAFT)
        url = "/fi/ideat/{0}/gallup/{1}/avaa/".format(self.idea.pk, gallup.pk)
        resp = self.client.post(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "gallup/well.html")
        self.assertNotContains(resp, "Gallup on luonnostilassa.")
        self.assertNotContains(resp, "Gallup on suljettu.")
        gallup = Gallup.objects.get(pk=gallup.pk)
        self.assertEqual(gallup.is_draft(), False)
        self.assertEqual(gallup.is_open(), True)
        self.assertEqual(gallup.is_closed(), False)

    def test_close_gallup(self):
        self.client.login(
            username=self.idea.owners.first().username,
            password=DEFAULT_PASSWORD
        )
        gallup = Gallup.objects.create(idea=self.idea, status=Gallup.STATUS_OPEN)
        url = "/fi/ideat/{0}/gallup/{1}/sulje/".format(self.idea.pk, gallup.pk)
        resp = self.client.post(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "gallup/well.html")
        self.assertNotContains(resp, "Gallup on luonnostilassa.")
        self.assertContains(resp, "Gallup on suljettu.")
        gallup = Gallup.objects.get(pk=gallup.pk)
        self.assertEqual(gallup.is_draft(), False)
        self.assertEqual(gallup.is_open(), False)
        self.assertEqual(gallup.is_closed(), True)

    def test_delete_gallup(self):
        self.client.login(
            username=self.idea.owners.first().username,
            password=DEFAULT_PASSWORD
        )
        gallup = Gallup.objects.create(idea=self.idea)
        url = "/fi/ideat/{0}/gallup/{1}/poista/".format(self.idea.pk, gallup.pk)
        resp = self.client.post(url, follow=True)

        self.assertContains(resp, "Gallup poistettu.", status_code=200)
        exists = Gallup.objects.filter(pk=gallup.pk).exists()
        self.assertEqual(exists, False)
    
    def test_show_draft_as_admin(self):
        self.setUp_gallup()
        self.assertTrue(self.gallup.is_draft())

        admin = UserFactory(groups=[Group.objects.get(name=GROUP_NAME_ADMINS)])
        self.client.login(username=admin.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(self.idea.pk))
        self.assertContains(resp, "Gallup on luonnostilassa.")
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_draft_as_moderator(self):
        self.setUp_gallup()
        self.assertTrue(self.gallup.is_draft())

        moderator = UserFactory(groups=[Group.objects.get(name=GROUP_NAME_MODERATORS)])
        self.client.login(username=moderator.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(self.idea.pk))
        self.assertContains(resp, "Gallup on luonnostilassa.")
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_draft_as_owner(self):
        self.setUp_gallup()
        self.assertTrue(self.gallup.is_draft())

        owner = self.idea.owners.first()
        self.client.login(username=owner.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(self.idea.pk))
        self.assertContains(resp, "Gallup on luonnostilassa.")
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_draft_as_non_owner(self):
        self.setUp_gallup()
        self.assertTrue(self.gallup.is_draft())

        user = UserFactory()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(self.idea.pk))
        self.assertNotContains(resp, "Gallup on luonnostilassa.")
        self.assertNotContains(resp, "Question #1")
        self.assertNotContains(resp, "Question #2")
        self.assertNotContains(resp, "Option #1")
        self.assertNotContains(resp, "Option #2")
        self.assertNotContains(resp, "Option #3")
        self.assertNotContains(resp, "Option #4")

    def test_show_open_as_admin(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_OPEN
        self.gallup.save()
        idea = self.idea
        self.assertTrue(self.gallup.is_open())

        admin = UserFactory(groups=[Group.objects.get(name=GROUP_NAME_ADMINS)])
        self.client.login(username=admin.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(idea.pk))
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_open_as_moderator(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_OPEN
        self.gallup.save()
        idea = self.idea
        self.assertTrue(self.gallup.is_open())

        moderator = UserFactory(groups=[Group.objects.get(name=GROUP_NAME_MODERATORS)])
        self.client.login(username=moderator.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(idea.pk))
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_open_as_owner(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_OPEN
        self.gallup.save()
        idea = self.idea
        self.assertTrue(self.gallup.is_open())

        owner = self.idea.owners.first()
        self.client.login(username=owner.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(idea.pk))
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_open_as_non_owner(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_OPEN
        self.gallup.save()
        idea = self.idea
        self.assertTrue(self.gallup.is_open())

        user = UserFactory()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(idea.pk))
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_closed_as_admin(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_CLOSED
        self.gallup.save()
        idea = self.idea
        self.assertTrue(self.gallup.is_closed())

        admin = UserFactory(groups=[Group.objects.get(name=GROUP_NAME_ADMINS)])
        self.client.login(username=admin.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(idea.pk))
        self.assertContains(resp, "Gallup on suljettu.")
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_closed_as_moderator(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_CLOSED
        self.gallup.save()
        idea = self.idea
        self.assertTrue(self.gallup.is_closed())

        moderator = UserFactory(groups=[Group.objects.get(name=GROUP_NAME_MODERATORS)])
        self.client.login(username=moderator.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(idea.pk))
        self.assertContains(resp, "Gallup on suljettu.")
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_closed_as_owner(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_CLOSED
        self.gallup.save()
        idea = self.idea
        self.assertTrue(self.gallup.is_closed())

        owner = self.idea.owners.first()
        self.client.login(username=owner.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(idea.pk))
        self.assertContains(resp, "Gallup on suljettu.")
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")

    def test_show_closed_as_non_owner(self):
        self.setUp_gallup()
        self.gallup.status = Gallup.STATUS_CLOSED
        self.gallup.save()
        idea = self.idea
        self.assertTrue(self.gallup.is_closed())

        user = UserFactory()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        resp = self.client.get("/fi/ideat/{}/".format(idea.pk))
        self.assertContains(resp, "Gallup on suljettu.")
        self.assertContains(resp, "Question #1")
        self.assertContains(resp, "Question #2")
        self.assertContains(resp, "Option #1")
        self.assertContains(resp, "Option #2")
        self.assertContains(resp, "Option #3")
        self.assertContains(resp, "Option #4")
