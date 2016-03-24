# coding=utf-8

from __future__ import unicode_literals

from operator import attrgetter
from uuid import uuid4

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError

from account.utils import get_client_identifier
from nkvote.models import Vote, Voter, Option, Gallup


def get_voter(request, create=True):
    """ Returns voter object for currently logged in user or non-logged in user.
        Use create=False if you only want to get the voter, but not to create one.
        Usually perms should use create=False. """
    voter = None

    try:
        user_id = request.user.pk
    except AttributeError:
        user_id = None

    if Voter.VOTER_COOKIE in request.COOKIES:
        cookie_voter_id = request.COOKIES[Voter.VOTER_COOKIE]
    else:
        cookie_voter_id = None

    if user_id:
        try:
            voter = Voter.objects.get(user_id=user_id)
        except Voter.DoesNotExist:
            voter = None  # Redundant?
            if cookie_voter_id:
                voter = Voter.objects.filter(
                    voter_id=request.COOKIES[Voter.VOTER_COOKIE]
                ).order_by("-user_id").first()
                if voter and not voter.user_id:
                    voter.user_id = user_id
                    voter.save()

    elif cookie_voter_id:
        voter = Voter.objects.filter(
            voter_id=request.COOKIES[Voter.VOTER_COOKIE]
        ).order_by("-user_id").first()

    if not voter and create:
        voter = Voter(user_id=user_id, voter_id=uuid4().hex)
        voter.save()

    """
    if Voter.VOTER_COOKIE in request.COOKIES:
        voter = Voter.objects.filter(
            voter_id=request.COOKIES[Voter.VOTER_COOKIE]
        ).order_by("-user_id").first()

    if voter and user_id and not voter.user_id:
        voter.user_id = user_id
        voter.save()

    elif not voter and user_id:
        voter, new = Voter.objects.get_or_create(
            user_id=user_id,
            defaults={"voter_id": uuid4().hex}
        )

    elif not voter and create:
        voter = Voter(voter_id=uuid4().hex)
        voter.save()



    if voter is None and user_id:
        voter, new = Voter.objects.get_or_create(
            user_id=user_id,
            defaults={"voter_id": uuid4().hex}
        )

    if voter is None and create:
        voter = Voter(voter_id=uuid4().hex)
        voter.save()
    """

    return voter


def get_voted_objects(request, objects, model_class):
    """ Returns the ideas/comments that have been voted by the current user in the
        request. Used to disable voting in the ideas/comments that have been voted
        already. """
    object_ids = map(attrgetter("pk"), objects)
    return list(Vote.objects.filter(
        voter=get_voter(request, create=False),
        object_id__in=object_ids,
        content_type=ContentType.objects.get_for_model(model_class)
    ).values_list("object_id", flat=True))


def answered_gallups(request):
    """ Returns list of gallups that the logged in user in request has already
        answered for. """
    return list(Gallup.objects.filter(answer__voter=get_voter(request, create=False)))


def answered_gallup(request, gallup):
    """ Returns true/false if a voted gallup is found on given id. """
    if gallup.answer_set.filter(voter=get_voter(request, create=False)):
        return True
    else:
        return False


def answered_options(request):
    """ Returns list of options that the logged in user in request has already
        answered for. """
    return list(Option.objects.filter(answer__voter=get_voter(request, create=False)))


def vote(request, target_class, object_pk, choice):
    voter = get_voter(request)
    client_identifier = get_client_identifier(request)
    content_object = target_class._default_manager.get(pk=object_pk)
    try:
        with transaction.atomic():
            vote_object = Vote(
                voter=voter,
                client_identifier=client_identifier,
                content_object=content_object,
                choice=choice,
            )
            vote_object.save()
            return vote_object
    except IntegrityError:
        return False


def get_vote(request, target_class, object_pk):
    try:
        vote_object = Vote.objects.get(
            voter=get_voter(request, create=False),
            object_id=object_pk,
            content_type=ContentType.objects.get_for_model(target_class)
        )
    except Vote.DoesNotExist:
        return None
    else:
        return vote_object


def get_votes(request, target_class, object_pk_list):
    votes = Vote.objects.filter(
        voter=get_voter(request, create=False),
        object_id__in=object_pk_list,
        content_type=ContentType.objects.get_for_model(target_class)
    )
    return votes


def set_vote_cookie(request, response, voter_id):
    response.set_cookie(
        Voter.VOTER_COOKIE,
        voter_id,
        httponly=True,
        secure=request.is_secure()
    )
    return response
