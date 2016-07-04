# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.db.models.expressions import F
from django.utils.translation import ugettext_lazy as _

from libs.formidable.forms.fields import InlineFormSetField
from libs.formidable.forms.forms import FormidableModelForm
from libs.formidable.forms.widgets import BootstrapInlineFormSetWidget
from nuka.forms.widgets import MultiLingualWidgetWithTranslatedNotification, \
    MultiLingualWidget

from . import models



class SurveyElementFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(SurveyElementFormMixin, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            del self.fields["order"]

    def save(self, commit=True):
        obj = super(SurveyElementFormMixin, self).save(commit=False)

        if commit is True:
            order = self.cleaned_data.get("order")
            if order:
                models.SurveyElement.objects \
                    .filter(survey_id=obj.survey_id, order__gte=order) \
                    .update(order=F("order") + 1)
                obj.order = order
            obj.save()
            self.save_m2m()

        return obj


class SurveySubtitleForm(SurveyElementFormMixin, forms.ModelForm):
    order = forms.IntegerField(min_value=0, required=False,
                               widget=forms.HiddenInput(attrs={"class": "order"}))

    class Meta:
        fields = ("text",)
        widgets = {
            'text': MultiLingualWidget
        }
        model = models.SurveySubtitle


class SurveyOptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SurveyOptionForm, self).__init__(*args, **kwargs)
        self.fields["text"].required = True

    class Meta:
        model = models.SurveyOption
        fields = ("text",)


class SurveyQuestionForm(SurveyElementFormMixin, FormidableModelForm):
    order = forms.IntegerField(min_value=0, required=False,
                               widget=forms.HiddenInput(attrs={"class": "order"}))
    options = InlineFormSetField(
        form_class=SurveyOptionForm, related_name="question", can_delete=True,
        widget=BootstrapInlineFormSetWidget, min_forms=2, initial_forms=2,
        widget_kwargs={
            "formset_context": {"add_form_label": _("Lisää vaihtoehto")},
            "form_context": {"delete_form_label": _("Poista vaihtoehto")},
        },
        label=_("Kysymyksen vastausvaihtoehdot")
    )

    def __init__(self, question_type, *args, **kwargs):
        super(SurveyQuestionForm, self).__init__(*args, **kwargs)
        if question_type in [models.SurveyQuestion.TYPE_TEXT,
                             models.SurveyQuestion.TYPE_NUMBER]:
            del self.fields["options"]

    class Meta:
        model = models.SurveyQuestion
        fields = ("text", "instruction_text", "required", "type")
        widgets = {
            "type": forms.HiddenInput(),
            'text': MultiLingualWidgetWithTranslatedNotification,
            'instruction_text': MultiLingualWidgetWithTranslatedNotification,
        }


# Survey answer forms.


class BaseSurveyQuestionAnswerForm(forms.Form):
    def __init__(self, question, disabled=False, *args, **kwargs):
        super(BaseSurveyQuestionAnswerForm, self).__init__(*args, **kwargs)
        self.question = question
        self.fields["answer"].label = self.question.text
        self.fields["answer"].instruction_text = self.question.instruction_text
        if disabled is True:
            self.fields["answer"].widget.attrs["disabled"] = "disabled"


class SurveyQuestionTextAnswerForm(BaseSurveyQuestionAnswerForm):
    answer = forms.CharField(
        #max_length=255,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": ""}),
        label=False
    )

    def __init__(self, *args, **kwargs):
        super(SurveyQuestionTextAnswerForm, self).__init__(*args, **kwargs)
        if not self.question.required:
            self.fields["answer"].required = False

    def save(self, submission):
        return models.SurveyAnswer.objects.create(submission=submission,
                                                  question=self.question,
                                                  text=self.cleaned_data["answer"])


class SurveyQuestionNumberAnswerForm(BaseSurveyQuestionAnswerForm):
    answer = forms.FloatField(label=False, help_text=_("Vastauksen on oltava numero."),
                              widget=forms.TextInput(attrs={"placeholder": ""}))

    def __init__(self, *args, **kwargs):
        super(SurveyQuestionNumberAnswerForm, self).__init__(*args, **kwargs)
        if not self.question.required:
            self.fields["answer"].required = False

    def save(self, submission):
        return models.SurveyAnswer.objects.create(submission=submission,
                                                  question=self.question,
                                                  text=self.cleaned_data["answer"])


class SurveyQuestionMultipleOptionAnswerForm(BaseSurveyQuestionAnswerForm):
    def __init__(self, *args, **kwargs):
        super(SurveyQuestionMultipleOptionAnswerForm, self).__init__(*args, **kwargs)
        if not self.question.required:
            self.fields["answer"].required = False
        self.fields["answer"].choices = [(option.pk, option.text)
                                         for option in self.question.options.all()]


class SurveyQuestionRadioAnswerForm(SurveyQuestionMultipleOptionAnswerForm):
    answer = forms.ChoiceField(choices=(), label=False, widget=forms.RadioSelect)

    def save(self, submission):
        option_id = self.cleaned_data["answer"]
        if not option_id:
            option_id = None
        submission.answers.create(question=self.question, option_id=option_id)


class SurveyQuestionCheckboxAnswerForm(SurveyQuestionMultipleOptionAnswerForm):
    answer = forms.MultipleChoiceField(choices=(), label=False,
                                       widget=forms.CheckboxSelectMultiple)

    def save(self, submission):
        option_ids = self.cleaned_data["answer"]
        if not option_ids:
            submission.answers.create(question=self.question, option_id=None)
        else:
            for option_id in option_ids:
                submission.answers.create(question=self.question, option_id=option_id)


class SurveyFormset(object):
    def __init__(self, survey, data=None, initial=None, disabled=False):
        self.survey = survey
        self.data = None
        self.initial = initial or {}
        self.disabled = disabled
        self.forms = None
        self.errors = None

        questions = dict(
            [(question.pk, question) for question in self.survey.elements.questions()]
        )

        if data is not None:
            self.data = {}
            for key in data:
                # hack if javascript disabled
                if key == 'csrfmiddlewaretoken':
                    continue
                question_id = int(key.replace("question_", "").replace("-answer", ""))
                question = questions[question_id]

                if question.type in question.TYPE_MULTIPLE_VALUES:
                    value = data.getlist(key)
                else:
                    value = data.get(key)

                if question_id not in self.data:
                    self.data[question_id] = {key: value}
                else:
                    self.data[question_id][key] = value

    def __getitem__(self, item):
        if self.forms is None:
            self.create_forms()
        return self.forms[item]

    def create_forms(self):
        # Parses the given data and creates the forms.
        self.forms = {}
        for question in self.survey.elements.questions():
            form_class = QUESTION_ANSWER_FORMS[question.type]
            form_data = self.data.get(question.pk, {}) if self.data is not None else None
            prefix = "question_{}".format(question.pk)
            initial = self.initial.get(question.pk)
            self.forms[question.pk] = form_class(data=form_data, question=question,
                                                 prefix=prefix, initial=initial,
                                                 disabled=self.disabled)

    def validate(self):
        self.errors = {}
        for question_id, form in self.get_forms().iteritems():
            if form.is_valid() is False:
                self.errors[question_id] = form.errors

    def is_valid(self):
        if self.errors is None:
            self.validate()
        return not bool(self.errors)

    def save(self, submitter, client_identifier):
        submission = models.SurveySubmission.objects.create(
            survey=self.survey,
            submitter=submitter,
            client_identifier=client_identifier
        )
        for form in self.get_forms().values():
            form.save(submission)
        return submission

    def get_form(self, question):
        if self.forms is None:
            self.create_forms()
        return self.forms[question.pk]

    def get_forms(self):
        if self.forms is None:
            self.create_forms()
        return self.forms

    def disable(self):
        for form in self.get_forms().values():
            for field in form.fields.values():
                field.widget.attrs["disabled"] = "disabled"
        self.disabled = True


QUESTION_ANSWER_FORMS = {
    models.SurveyQuestion.TYPE_TEXT: SurveyQuestionTextAnswerForm,
    models.SurveyQuestion.TYPE_NUMBER: SurveyQuestionNumberAnswerForm,
    models.SurveyQuestion.TYPE_RADIO: SurveyQuestionRadioAnswerForm,
    models.SurveyQuestion.TYPE_CHECKBOX: SurveyQuestionCheckboxAnswerForm,
}
