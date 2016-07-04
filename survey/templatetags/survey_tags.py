# coding=utf-8

from __future__ import unicode_literals

from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from .. import models
from content.survey_perms import CanAnswerSurvey
from survey.forms import SurveyFormset
from survey.utils import survey_formset_initial, get_submitter



register = template.Library()


@register.assignment_tag
def survey_element_subtype_order(element):
    """
    Returns given element's order within its subtype (i.e. page, subtitle or question).
    """
    return models.SurveyElement.objects \
        .instance_of(type(element)) \
        .filter(survey=element.survey, order__lt=element.order) \
        .count() + 1


@register.assignment_tag
def survey_element_subtype_count(element):
    """
    Returns given element's order within its subtype (i.e. page, subtitle or question).
    """
    return models.SurveyElement.objects \
        .instance_of(type(element)) \
        .filter(survey=element.survey) \
        .count()


@register.simple_tag(takes_context=True)
def render_survey_element(context, element=None):
    """
    Renders the survey element's form depending on type of the element.
    If no element is given, assumes it is found from the context with name "element".
    """
    # TODO: Flexible way to render the elements.

    if element is None:
        element = context.get("element")

    if type(element) == models.SurveyQuestion:

        # fallback if context does not contain formset
        if 'formset' not in context:
            submitter = get_submitter(context['request'])
            initial = survey_formset_initial(element.survey, submitter)
            can_answer = CanAnswerSurvey(
                request=context['request'], obj=element.survey).is_authorized()
            formset = SurveyFormset(survey=element.survey, initial=initial,
                                 disabled=can_answer is False)
            form = formset[element.pk]
        else:
            form = context["formset"][element.pk]
        context['form'] = form
        return render_to_string("survey/answer_mode/question.html",
                                #context={"form": form},
                                context_instance=context)

    elif type(element) == models.SurveyPage:
        return render_to_string("survey/answer_mode/page.html",
                                context_instance=context)

    elif type(element) == models.SurveySubtitle:
        return render_to_string("survey/answer_mode/subtitle.html",
                                context_instance=context)

    return ""


@register.simple_tag(takes_context=True)
def render_template_to_variable(context, **kwargs):
    for variable_name, template_name in kwargs.iteritems():
        context[variable_name] = render_to_string(template_name, context_instance=context)
    return ""


@register.simple_tag(takes_context=True)
def render_question_answers(context, question, paginate=True):
    context_dict = {"question": question, "request": context["request"]}

    if 'no_pagination' in context:
        context_dict.update({'no_pagination': context['no_pagination']})
    context = context_dict

    if question.type == models.SurveyQuestion.TYPE_TEXT:
        template_name = "survey/question_answers_text.html"
        context["paginate"] = paginate
    elif question.type == models.SurveyQuestion.TYPE_NUMBER:
        template_name = "survey/question_answers_number.html"
    elif question.type == models.SurveyQuestion.TYPE_RADIO:
        template_name = "survey/question_answers_radio.html"
    elif question.type == models.SurveyQuestion.TYPE_CHECKBOX:
        template_name = "survey/question_answers_checkbox.html"
    else:
        return ""
    return render_to_string(template_name, context)


@register.filter(name="is_answered")
def survey_is_answered(survey, request):
    submitter = get_submitter(request, create=False)
    return survey.submissions.filter(submitter=submitter).exists()


@register.inclusion_tag("survey/question_answers_text_results.html", takes_context=True)
def show_text_answers(context, question, paginate=True):
    answers = question.answers.exclude(text="")

    if paginate:
        answers = answers.paginate()
        pagination_url = reverse(
            "survey:question_answers",
            kwargs={"survey_id": question.survey_id, "question_id": question.pk}
        )
        request = context["request"]
        if request.GET:
            pagination_url = "{}?{}".format(pagination_url, request.GET.urlencode())

        return {
            "answers": answers,
            "paginate": paginate,
            "pagination_url": pagination_url
        }

    return {"answers": answers}
