# coding=utf-8

from __future__ import unicode_literals

from django.utils.module_loading import import_string

from .conf import config
from .models import SurveySubmission, SurveySubmitter, SurveyQuestion


def survey_formset_initial(survey, submitter):
    try:
        submission = survey.submissions.get(submitter=submitter)
    except SurveySubmission.DoesNotExist:
        return {}

    initial = {}
    for answer in submission.answers.all():
        question_type = answer.question.type
        attr = "text" if answer.text is not None else "option_id"
        value = getattr(answer, attr)

        if question_type in SurveyQuestion.TYPE_MULTIPLE_VALUES:
            value = [value]

        if answer.question_id not in initial:
            initial[answer.question_id] = {"answer": value}
        else:
            initial[answer.question_id]["answer"].extend(value)

    return initial


def get_submitter(request, create=True):
    """
    Returns survey submitter object for currently logged in user or non-logged in user.
    Use create=False if you only want to get the voter, but not to create one.
    Usually perms should use create=False.
    """
    submitter = None

    try:
        user_id = request.user.pk
    except AttributeError:
        user_id = None

    cookie_submitter_id = request.COOKIES.get(SurveySubmitter.SUBMITTER_COOKIE, None)

    if user_id:
        try:
            submitter = SurveySubmitter.objects.get(user_id=user_id)
        except SurveySubmitter.DoesNotExist:
            if cookie_submitter_id:
                submitter = SurveySubmitter.objects \
                    .filter(submitter_id=cookie_submitter_id) \
                    .order_by("-user_id") \
                    .first()
                if submitter and not submitter.user_id:
                    submitter.user_id = user_id
                    submitter.save()

    elif cookie_submitter_id:
        submitter = SurveySubmitter.objects \
            .filter(submitter_id=cookie_submitter_id) \
            .order_by("-user_id") \
            .first()

    if not submitter and create:
        submitter = SurveySubmitter.objects.create(user_id=user_id)

    return submitter


def set_submitter_cookie(request, response, submitter_id):
    response.set_cookie(SurveySubmitter.SUBMITTER_COOKIE, submitter_id, httponly=True,
                        secure=request.is_secure())
    return response


def get_client_identifier(request):
    return import_string(config.get_client_identifier_path)(request)
