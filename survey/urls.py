# coding=utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url, include

from libs.djcontrib.conf.urls import decorated_patterns
from libs.djcontrib.utils.decorators import combo, obj_by_pk
from libs.permitter.decorators import check_perm

from . import views
from .models import Survey, SurveyQuestion
from .perms import CanEditSurvey, CanAnswerSurvey, ShowSurveyResults


survey_as_obj = obj_by_pk(Survey, "survey_id")
question_as_obj = obj_by_pk(SurveyQuestion, "question_id")

urlpatterns = decorated_patterns(
    "",
    combo(survey_as_obj, check_perm(CanEditSurvey)),

    url(r"^kysely/(?P<survey_id>\d+)/", include(patterns(
        "",
        url(r"^elementti/(?P<element_id>\d+)/", include(patterns(
            "",
            url(r"^nosta/$",
                views.SurveyElementMoveView.as_view(direction="up"), name="move_up"),
            url(r"^laske/$",
                views.SurveyElementMoveView.as_view(direction="down"), name="move_down"),
            url(r"^poista/$", views.SurveyElementDeleteView.as_view(), name="delete"),
        ), namespace="element")),

        url(r"^sivu/uusi/$", views.SurveyPageCreateView.as_view(), name="create_page"),

        url(r"^valiotsikko/", include(patterns(
            "",
            url(r"^uusi/$",
                views.SurveySubtitleFormView.as_view(), name="create_subtitle"),
            url(r"^(?P<subtitle_id>\d+)/muokkaa/$",
                views.SurveySubtitleFormView.as_view(), name="update_subtitle"),
            url(r"^(?P<subtitle_id>\d+)/$",
                views.SurveySubtitleAnswerView.as_view(), name="subtitle"),
        ))),

        url(r"^kysymys/", include(patterns(
            "survey.views",
            url(
                name="question",
                regex="^(?P<question_id>\d+)/$",
                view="question_answer",
            ),
            url(
                name="update_question",
                regex="^(?P<question_id>\d+)/muokkaa/$",
                view="question_form",
            ),
            url(
                name="create_text_question",
                regex=r"^uusi/teksti/$",
                view="question_form_text",
            ),
            url(
                name="create_number_question",
                regex="^uusi/numero/$",
                view="question_form_number",
            ),
            url(
                name="create_radio_question",
                regex="^uusi/yksivalinta/$",
                view="question_form_radio",
            ),
            url(
                name="create_checkbox_question",
                regex="^uusi/monivalinta/$",
                view="question_form_checkbox",
            ),
        ))),
    ))),
)

urlpatterns += [
    url(r"^kysely/(?P<survey_id>\d+)/laheta/$",
        survey_as_obj(check_perm(CanAnswerSurvey)(views.SurveySubmissionView.as_view())),
        name="submit"),
    url(r"^kysely/(?P<survey_id>\d+)/kysymys/(?P<question_id>\d+)/vastaukset/$",
        survey_as_obj(check_perm(ShowSurveyResults)
                      (views.SurveyQuestionAnswerListView.as_view())),
        name="question_answers"),
]
