# coding=utf-8

from __future__ import unicode_literals

from datetime import datetime
import json

from django.db import transaction
from django.db.utils import IntegrityError
from django.http.response import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse
from wkhtmltopdf.views import PDFTemplateView

from content.models import Idea
from account.utils import get_client_identifier
from content.pdfprint import BetterPDFTemplateResponse

from .models import Vote, Voter, Gallup, Question, Option, Answer
from django.conf import settings
from .utils import get_voter, answered_options, answered_gallups


class VoteView(TemplateView):

    choice = Vote.VOTE_NONE
    klass = None
    pk_url_kwarg = "pk"

    def info_given(self):
        return self.choice in (Vote.VOTE_UP, Vote.VOTE_DOWN)

    def get_content_object(self):
        return self.klass._default_manager.get(pk=self.kwargs[self.pk_url_kwarg])

    def vote(self, request, **kwargs):
        if not self.info_given():
            return JsonResponse({
                "success": False,
                "message": "Necessary information was not given."
            })

        voter = get_voter(request)
        content_object = self.get_content_object()
        try:
            with transaction.atomic():
                vote_object = Vote(
                    voter=voter,
                    client_identifier=get_client_identifier(request),
                    content_object=content_object,
                    choice=self.choice,
                )
                vote_object.save()
        except IntegrityError:
            pass

        response = self.render_to_response({
            "votable_object": content_object,
            "voted": True,
            "vote_choice": self.choice
        })
        response.set_cookie(
            Voter.VOTER_COOKIE, voter.voter_id, httponly=True, secure=request.is_secure()
        )
        return response

    def post(self, request, **kwargs):
        return self.vote(request, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed()


class GallupFormView(TemplateView):
    template_name = "gallup/form.html"
    http_method_names = ["get", "post"]

    def get_questions(self, post_data):
        """ Returns a list of questions from the post data. The questions also have
            attached their respective options with their data. """
        try:
            del post_data["csrfmiddlewaretoken"]
        except KeyError:
            pass
        del post_data["default_view"]
        question_inputs = list()
        questions_db_id = list()
        option_inputs = list()
        options_db_id = list()

        db_id_tag = "db_id"
        option_tag = "_o-"

        # Iterate through the post data to find questions, options and db ids.
        for key, value in post_data.iteritems():

            # If value is not set, skip it.
            if not value:
                continue

            # Get the language code out of the key if it's not databse id.
            if db_id_tag not in key:
                language_code = key[-2:]
                key = key[:-3]

            # Question database id.
            if db_id_tag in key and option_tag not in key:
                questions_db_id.append({
                    "question_seq": int(key[8:]),
                    "id": int(value)
                })

            # Option database id.
            elif db_id_tag in key and option_tag in key:
                # Question's sequence starts from 8 and ends at option tag.
                question_seq_begin = 8
                question_seq_end = key.index(option_tag)

                # Sequence starts from where option tag begins +
                option_seq_begin = key.index(option_tag) + 3

                options_db_id.append({
                    "question_seq": int(key[question_seq_begin:question_seq_end]),
                    "option_seq": int(key[option_seq_begin:]),
                    "id": int(value)
                })

            # Question text.
            elif option_tag not in key:
                question_inputs.append({
                    "id": None,
                    "seq_number": int(key[2:]),
                    "text": value,
                    "options": [],
                    "language": language_code
                })

            # Option text.
            elif option_tag in key:
                # Question's seq begins at 2 and ends at option's beginning.
                question_seq_begin = 2
                question_seq_end = key.index(option_tag)

                # Option's seq begins at option tag + 3.
                option_seq_begin = key.index(option_tag) + 3

                option_inputs.append({
                    "id": None,
                    "question_seq": int(key[question_seq_begin:question_seq_end]),
                    "seq_number": int(key[option_seq_begin:]),
                    "text": value,
                    "language": language_code
                })

        # Loop through the question db ids and add them to the respective questions.
        for db_id_data in questions_db_id:
            for question in question_inputs:
                if question["seq_number"] == db_id_data["question_seq"]:
                    question["id"] = db_id_data["id"]
                    break

        # Loop through the option db ids and add them to the respective options.
        for db_id_data in options_db_id:
            for option in option_inputs:
                if option["seq_number"] == db_id_data["option_seq"]:
                    if option["question_seq"] == db_id_data["question_seq"]:
                        option["id"] = db_id_data["id"]
                        break

        # Merge questions language versions to one dictionary item.
        questions = dict()
        for question in question_inputs:
            if question["seq_number"] not in questions:
                questions[question["seq_number"]] = {
                    "id": question["id"],
                    "seq_number": question["seq_number"],
                    "text": {question["language"]: question["text"]},
                    "options": []
                }
            else:
                questions[question["seq_number"]]["text"].update(
                    {question["language"]: question["text"]}
                )

        # Merge options language versions to one dictionary item.
        options = dict()
        for option in option_inputs:
            option_id = "{}-{}".format(option["question_seq"], option["seq_number"])
            if option_id not in options:
                options[option_id] = {
                    "id": option["id"],
                    "question_seq": option["question_seq"],
                    "seq_number": option["seq_number"],
                    "text": {option["language"]: option["text"]},
                }
            else:
                options[option_id]["text"].update({option["language"]: option["text"]})

        # Loop through the options and add them to the respective questions.
        for option in options.values():
            for question in questions.values():
                if option["question_seq"] == question["seq_number"]:
                    if option not in question["options"]:
                        question["options"].append(option)
                    break

        return questions.values()

    def save(self, questions, default_view):
        idea = Idea.unmoderated_objects.get(pk=self.kwargs["initiative_id"])

        try:
            gallup = Gallup.objects.get(pk=self.kwargs["gallup_id"])
        except KeyError:
            gallup = Gallup.objects.create(idea=idea)

        # Get the old questions and options for reference later on.
        old_questions = list(gallup.question_set.all())
        old_options = {}
        for old_question in old_questions:
            old_options[old_question.id] = list(old_question.option_set.all())

        new_questions = list()
        new_options = list()

        # Loop the questions.
        for question_data in questions:
            # If id is set, we update the old question.
            if question_data["id"]:
                question = Question.objects.get(pk=question_data["id"])
                question.seq_number = question_data["seq_number"]
                question.text = question_data["text"]
                question.save()
                new_questions.append(question)

            # If id is not set, we create new question.
            else:
                question = Question.objects.create(
                    gallup=gallup,
                    seq_number=question_data["seq_number"],
                    text=question_data["text"],
                )

            # Loop through the options.
            for option_data in question_data["options"]:
                # If id is set, update the old option.
                if option_data["id"]:
                    option = Option.objects.get(pk=option_data["id"])
                    option.seq_number = option_data["seq_number"]
                    option.text = option_data["text"]
                    option.save()
                    new_options.append(option)

                # If id is not set, create a new option.
                else:
                    Option.objects.create(
                        question=question,
                        seq_number=option_data["seq_number"],
                        text=option_data["text"],
                    )

        # Loop through the old questions to find the ones to delete.
        for old_question in old_questions:
            question_found = False
            for new_question in new_questions:
                if old_question.id == new_question.id:
                    question_found = True
                    break

            # If the old question was not found in the new ones, delete it.
            if not question_found:
                old_question.delete()
                continue

            # If the question still exists, check if its options have been deleted.
            for old_option in old_options[old_question.id]:
                option_found = False
                for new_option in new_options:
                    if old_option.id == new_option.id:
                        option_found = True
                        break

                # If the old option was not found in the new ones, delete it.
                if not option_found:
                    old_option.delete()

        # Add/update the default view shown on the gallup.
        if default_view == "questions":
            gallup.default_view = Gallup.DEFAULT_QUESTIONS
            gallup.save()
        elif default_view == "results":
            gallup.default_view = Gallup.DEFAULT_RESULTS
            gallup.save()

        messages.success(self.request, ugettext('Gallup tallennettu.'))
        return redirect(
            reverse("content:idea_detail", args=[idea.id])
            + "#gallup-{0}".format(gallup.id)
        )

    def post(self, *args, **kwargs):
        questions = self.get_questions(self.request.POST.copy())
        return self.save(questions, self.request.POST["default_view"])

    def get_context_data(self, **kwargs):
        context = super(GallupFormView, self).get_context_data(**kwargs)
        try:
            context["gallup"] = get_object_or_404(Gallup, pk=self.kwargs["gallup_id"])
        except KeyError:
            pass
        context["languages"] = settings.LANGUAGES
        context["active_language"] = self.request.LANGUAGE_CODE
        lang_dict = [dict([("code", k), ("label", v)]) for k, v in settings.LANGUAGES]
        context["languages_json"] = json.dumps(lang_dict, ensure_ascii=False)
        return context


class NewGallupQuestionView(TemplateView):
    template_name = "gallup/form/question.html"

    def get_context_data(self, **kwargs):
        context = super(NewGallupQuestionView, self).get_context_data(**kwargs)
        context["question_seq"] = self.request.GET.get("question_seq")
        context["languages"] = settings.LANGUAGES
        return context


class NewGallupOptionView(TemplateView):
    template_name = "gallup/form/option.html"

    def get_context_data(self, **kwargs):
        context = super(NewGallupOptionView, self).get_context_data(**kwargs)
        context["question_seq"] = self.request.GET.get("question_seq")
        context["option_seq"] = self.request.GET.get("option_seq")
        context["languages"] = settings.LANGUAGES
        return context


class GallupResultsView(TemplateView):
    template_name = "gallup/well.html"
    http_method_names = ["get", "post"]

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        context["show_results"] = True
        context["answered_options"] = answered_options(self.request)
        context["answered_gallups"] = answered_gallups(self.request)
        return TemplateResponse(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        # Get the chosen options ids.
        post = self.request.POST.copy()
        try:
            del post["csrfmiddlewaretoken"]
        except KeyError:
            pass
        choice_ids = map(lambda v: int(v), post.values())

        # Create a new answer and add the voter and the choices.
        voter = get_voter(self.request)
        answer = Answer.objects.create(
            gallup_id=self.kwargs["gallup_id"],
            voter=voter,
            client_identifier=get_client_identifier(self.request)
        )
        choices = Option.objects.filter(pk__in=choice_ids).all()
        answer.choices.add(*choices)

        context = self.get_context_data()
        context["show_results"] = True
        context["disabled"] = True
        context["answered_options"] = choices
        response = TemplateResponse(self.request, self.template_name, context)
        response.set_cookie(Voter.VOTER_COOKIE, voter.voter_id)
        return response

    def get_context_data(self, **kwargs):
        context = super(GallupResultsView, self).get_context_data(**kwargs)
        context["gallup"] = Gallup.objects.get(pk=self.kwargs["gallup_id"])
        context["absolute_uri"] = self.request.build_absolute_uri(
            reverse("content:idea_detail", args=[self.kwargs["initiative_id"]])
        )
        return context


class DeleteGallupView(DeleteView):
    model = Gallup
    pk_url_kwarg = "gallup_id"
    template_name = "gallup/confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, ugettext('Gallup poistettu.'))
        kwargs = {"initiative_id": self.kwargs["initiative_id"]}
        return reverse("content:idea_detail", kwargs=kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeleteGallupView, self).get_context_data(**kwargs)
        context["idea_id"] = self.kwargs["initiative_id"]
        return context


class GallupStatusChangeView(TemplateView):
    template_name = "gallup/well.html"
    http_method_names = ["post"]
    status = None

    def post(self, *args, **kwargs):
        if not self.status:
            return self.render_to_response(self.get_context_data())

        context = self.get_context_data()
        gallup = context["gallup"]
        if self.status == Gallup.STATUS_OPEN:
            gallup.status = Gallup.STATUS_OPEN
            gallup.opened = datetime.now()
        elif self.status == gallup.STATUS_CLOSED:
            gallup.status = Gallup.STATUS_CLOSED
            gallup.closed = datetime.now()
        gallup.save()

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(GallupStatusChangeView, self).get_context_data(**kwargs)
        context["gallup"] = Gallup.objects.get(pk=self.kwargs["gallup_id"])
        if self.status == Gallup.STATUS_OPEN and context["gallup"].default_results():
            context["show_results"] = True
        elif self.status == Gallup.STATUS_CLOSED:
            context["disabled"] = True
            context["show_results"] = True
        context["absolute_uri"] = self.request.build_absolute_uri(
            reverse("content:idea_detail", args=[self.kwargs["initiative_id"]])
        )
        return context


class GallupResultsToPdfView(PDFTemplateView):
    model = Gallup
    template_name = 'gallup/results_pdf.html'
    response_class = BetterPDFTemplateResponse

    filename = 'nuortenideat_gallup_tulokset_{}.pdf'.format(datetime.now().date())
    show_content_in_browser = False
    cmd_options = {
        'viewport-size': '1280x1024',
        'orientation': 'portrait',
        'enable-internal-links': True,
        'enable-external-links': True,
        'load-media-error-handling': 'ignore',
        'load-error-handling': 'ignore',
    }

    def get_idea(self):
        return get_object_or_404(Idea, pk=self.kwargs['initiative_id'])

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(GallupResultsToPdfView, self).get_context_data(**kwargs)
        context['object'] = self.get_idea()
        context["gallup"] = Gallup.objects.get(pk=self.kwargs["gallup_id"])
        context["show_results"] = True
        context["disabled"] = True
        context["absolute_uri"] = self.request.build_absolute_uri(
            reverse("content:idea_detail", args=[self.kwargs["initiative_id"]])
        )
        return context