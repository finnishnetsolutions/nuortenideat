# coding=utf-8

from __future__ import unicode_literals

from httplib import RESET_CONTENT

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models.aggregates import Max
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic.base import View, ContextMixin, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from . import models, forms
from survey.default_perms import SurveyAnsweredByUser
from survey.models import SurveySubmitter
from .utils import set_submitter_cookie, get_submitter, get_client_identifier


class SurveyElementMoveView(SingleObjectMixin, View):
    model = models.SurveyElement
    queryset = models.SurveyElement.objects.non_polymorphic()
    pk_url_kwarg = "element_id"
    direction = None

    def post(self, request, *args, **kwargs):
        element = self.get_object()

        if self.direction == "up":
            element.up()
        elif self.direction == "down":
            element.down()
        else:
            return HttpResponse("Unkown direction.", status=400)

        return HttpResponse(status=RESET_CONTENT)


class SurveyElementDeleteView(DeleteView):
    model = models.SurveyElement
    queryset = models.SurveyElement.objects.non_polymorphic()
    pk_url_kwarg = "element_id"

    def delete(self, request, *args, **kwargs):
        element = self.get_object()
        element.delete()
        return HttpResponse(status=RESET_CONTENT)


class SurveyPageCreateView(CreateView):
    model = models.SurveyPage
    fields = ["survey"]
    template_name = "survey/answer_mode/page.html"
    context_object_name = "element"
    http_method_names = ["post"]

    def get_context_data(self, **kwargs):
        context = super(SurveyPageCreateView, self).get_context_data(**kwargs)
        context["edit_mode"] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(SurveyPageCreateView, self).get_form_kwargs()
        kwargs["data"] = kwargs["data"].copy()
        kwargs["data"]["survey"] = self.kwargs["survey_id"]
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_response(self.get_context_data(form=form))


class SurveySubtitleFormView(UpdateView):
    """ Create and update view for survey subtitles. """
    queryset = models.SurveySubtitle.objects.select_related("survey")
    form_class = forms.SurveySubtitleForm
    pk_url_kwarg = "subtitle_id"
    template_name = "survey/edit_mode/subtitle.html"
    context_object_name = "element"

    def get_prefix_id(self):
        given_prefix_id = self.request.GET.get("prefix_id")
        if given_prefix_id is not None:
            return given_prefix_id
        given_prefix_id = self.request.POST.get("prefix_id")
        if given_prefix_id is not None:
            return given_prefix_id

    def get_prefix(self):
        given_prefix_id = self.get_prefix_id()
        if given_prefix_id is not None:
            return "new_subtitle_{}".format(given_prefix_id)
        return "subtitle_{}".format(self.object.pk)

    def get_initial(self):
        initial = super(SurveySubtitleFormView, self).get_initial()
        if self.request.method.lower() == "get" and self.has_url_pk() is False:
            initial["order"] = models.SurveyElement.objects \
                .filter(survey_id=self.kwargs["survey_id"]) \
                .aggregate(Max("order")) \
                .get("order__max")

            if initial['order'] is int:
                initial['order'] += 1

        initial["prefix_id"] = self.get_prefix_id() or self.object.pk
        return initial

    def get_context_data(self, **kwargs):
        context = super(SurveySubtitleFormView, self).get_context_data(**kwargs)
        context["survey_id"] = self.kwargs["survey_id"]
        context["edit_mode"] = True
        context.setdefault("new", True)
        context["prefix_id"] = self.get_prefix_id() or self.object.pk
        return context

    def get_object(self, queryset=None):
        if self.has_url_pk() is False:
            return models.SurveySubtitle(survey_id=self.kwargs["survey_id"])
        return super(SurveySubtitleFormView, self).get_object(queryset)

    def has_url_pk(self):
        return bool(self.kwargs.get(self.pk_url_kwarg, None))

    def form_invalid(self, form):
        context = self.get_context_data(form=form, new=self.has_url_pk())
        return self.render_to_response(context)

    def form_valid(self, form):
        self.object = form.save()
        self.template_name = "survey/answer_mode/subtitle.html"
        context = self.get_context_data(form=form, new=False)
        return self.render_to_response(context)


class SurveySubtitleAnswerView(DetailView):
    model = models.SurveySubtitle
    template_name = "survey/answer_mode/subtitle.html"
    pk_url_kwarg = "subtitle_id"
    context_object_name = "element"

    def get_context_data(self, **kwargs):
        context = super(SurveySubtitleAnswerView, self).get_context_data(**kwargs)
        context["edit_mode"] = True
        return context


class SurveyQuestionFormView(UpdateView):
    """
    Expects type parameter in get or post data, depending on the request method.
    """
    queryset = models.SurveyQuestion.objects.select_related("survey")
    form_class = forms.SurveyQuestionForm
    pk_url_kwarg = "question_id"
    template_name = "survey/edit_mode/question.html"
    context_object_name = "element"
    question_type = None

    def get_prefix_id(self):
        given_prefix_id = self.request.GET.get("prefix_id")
        if given_prefix_id is not None:
            return given_prefix_id
        given_prefix_id = self.request.POST.get("prefix_id")
        if given_prefix_id is not None:
            return given_prefix_id

    def get_prefix(self):
        given_prefix_id = self.get_prefix_id()
        if given_prefix_id is not None:
            return "new_question_{}".format(given_prefix_id)
        return "question_{}".format(self.object.pk)

    def get_initial(self):
        initial = super(SurveyQuestionFormView, self).get_initial()
        initial["type"] = self.get_question_type()
        if self.request.method.lower() == "get" and self.has_url_pk() is False:
            max_order = models.SurveyElement.objects \
                .filter(survey_id=self.kwargs["survey_id"]) \
                .aggregate(Max("order")) \
                .get("order__max")
            initial["order"] = max_order + 1 if max_order is not None else 0
        initial["prefix_id"] = self.get_prefix_id() or self.object.pk
        return initial

    def get_form_kwargs(self):
        kwargs = super(SurveyQuestionFormView, self).get_form_kwargs()
        kwargs["question_type"] = self.get_question_type()
        return kwargs

    def is_option_input(self):
        return self.get_question_type() in [models.SurveyQuestion.TYPE_CHECKBOX,
                                            models.SurveyQuestion.TYPE_RADIO]

    def get_question_type(self):
        if self.question_type:
            return self.question_type
        self.question_type = self.get_object().type
        return self.question_type

    def get_type_display(self):
        if self.question_type:
            return dict(models.SurveyQuestion.TYPE_CHOICES)[self.get_question_type()]
        return self.get_object().get_type_display()

    def get_context_data(self, **kwargs):
        context = super(SurveyQuestionFormView, self).get_context_data(**kwargs)
        context["is_option_input"] = self.is_option_input()
        context["question_type_display"] = self.get_type_display()
        context["survey_id"] = self.kwargs["survey_id"]
        context["edit_mode"] = True
        context.setdefault("new", True)
        context["prefix_id"] = self.get_prefix_id() or self.object.pk
        return context

    def get_object(self, queryset=None):
        if self.has_url_pk() is False:
            return models.SurveyQuestion(survey_id=self.kwargs["survey_id"])
        return super(SurveyQuestionFormView, self).get_object(queryset)

    def has_url_pk(self):
        return bool(self.kwargs.get(self.pk_url_kwarg, None))

    def form_invalid(self, form):
        context = self.get_context_data(form=form, new=not self.has_url_pk())
        return self.render_to_response(context)

    def form_valid(self, form):
        self.object = form.save()
        self.template_name = "survey/answer_mode/question.html"
        answer_form_class = forms.QUESTION_ANSWER_FORMS[self.object.type]
        form = answer_form_class(
            question=self.object,
            prefix="question_{}".format(self.object.pk)
        )
        context = self.get_context_data(form=form, new=False)
        return self.render_to_response(context)

question_form = SurveyQuestionFormView.as_view()
question_form_text = SurveyQuestionFormView.as_view(
    question_type=models.SurveyQuestion.TYPE_TEXT)
question_form_number = SurveyQuestionFormView.as_view(
    question_type=models.SurveyQuestion.TYPE_NUMBER)
question_form_radio = SurveyQuestionFormView.as_view(
    question_type=models.SurveyQuestion.TYPE_RADIO)
question_form_checkbox = SurveyQuestionFormView.as_view(
    question_type=models.SurveyQuestion.TYPE_CHECKBOX)


class SurveyQuestionAnswerView(DetailView):
    model = models.SurveyQuestion
    template_name = "survey/answer_mode/question.html"
    pk_url_kwarg = "question_id"
    context_object_name = "element"

    def get_context_data(self, **kwargs):
        context = super(SurveyQuestionAnswerView, self).get_context_data(**kwargs)
        context["edit_mode"] = True
        form_class = forms.QUESTION_ANSWER_FORMS[self.object.type]
        form = form_class(question=self.object,
                          prefix="question_{}".format(self.object.pk))
        context["form"] = form
        return context

question_answer = SurveyQuestionAnswerView.as_view()


class SurveySubmissionView(TemplateResponseMixin, ContextMixin, View):
    http_method_names = ["post"]
    template_name = "survey/survey_answer_form.html"
    survey = None

    def get_survey(self):
        if self.survey is None:
            self.survey = models.Survey.objects.get(pk=self.kwargs["survey_id"])
        return self.survey

    def get_formset_kwargs(self):
        return {"survey": self.get_survey(),
                "data": self.request.POST}

    def get_context_data(self, **kwargs):
        context = super(SurveySubmissionView, self).get_context_data(**kwargs)
        context["survey"] = self.get_survey()
        context["form_submitted"] = self.request.method.lower() == "post"
        return context

    def formset_invalid(self, formset):
        messages.error(self.request, _("Lomakkeessa oli virheitä. Tarkista kentät."))
        return self.render_to_response(self.get_context_data(formset=formset))

    def formset_valid(self, formset):
        submitter = get_submitter(self.request)
        client_identifier = get_client_identifier(self.request)
        formset.save(submitter, client_identifier)
        formset.disable()
        messages.success(self.request, _("Kiitos kyselyyn osallistumisesta."))
        response = self.render_to_response(self.get_context_data(formset=formset))
        self.request.COOKIES[SurveySubmitter.SUBMITTER_COOKIE] = submitter.submitter_id
        return set_submitter_cookie(self.request, response, submitter.submitter_id)

    def post(self, request, *args, **kwargs):
        formset = forms.SurveyFormset(**self.get_formset_kwargs())
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)


class SurveyQuestionAnswerListView(ListView):
    template_name = "survey/question_answers_text_results.html"
    paginate_by = models.SurveyAnswer.PAGINATE_BY
    question = None

    def get_queryset(self):
        question = models.SurveyQuestion.objects.get(pk=self.kwargs["question_id"])
        answers = question.answers.all()
        if question.type == question.TYPE_TEXT:
            answers = answers.exclude(text="")
        return answers

    def get_pagination_url(self):
        pagination_url = reverse(
            "survey:question_answers",
            kwargs={"survey_id": self.kwargs["survey_id"],
                    "question_id": self.kwargs["question_id"]}
        )
        if len(self.request.GET):
            pagination_url = "{}?{}".format(pagination_url, self.request.GET.urlencode())
        return pagination_url

    def get_context_data(self, **kwargs):
        context = super(SurveyQuestionAnswerListView, self).get_context_data(**kwargs)
        context["answers"] = context["page_obj"]
        context["paginate"] = True
        context["pagination_url"] = self.get_pagination_url()
        return context
