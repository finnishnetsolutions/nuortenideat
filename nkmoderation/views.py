# coding=utf-8

from __future__ import unicode_literals

from django.contrib import messages
from django.db import transaction
from django.db.utils import IntegrityError
from django.http.response import JsonResponse
from django.utils import timezone
from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.edit import CreateView
from django.utils.translation import ugettext as _

from libs.moderation.models import MODERATION_STATUS_REJECTED
from account.utils import get_client_identifier

from nkmoderation.models import ContentFlag

from .forms import FlagContentForm


class FlagContentView(CreateView):
    template_name = 'nkmoderation/flag_content_form.html'
    form_class = FlagContentForm

    @transaction.atomic()
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.content_type_id = self.kwargs['content_type_id']
        obj.object_id = self.kwargs['object_id']
        obj.client_identifier = get_client_identifier(self.request)
        if self.request.user.is_authenticated():
            obj.flagger = self.request.user
        try:
            obj.save()
        except IntegrityError:
            messages.error(self.request, _("Olet jo ilmoittanut kyseisen sisällön."))
            JsonResponse({'reload': True})

        messages.success(self.request, _("Kiitos ilmoituksesta. Ilmoitus on välitetty "
                                         "palvelun moderaattoreille."))
        return JsonResponse({'reload': True})


class ApproveModeratedObject(TemplateResponseMixin, View):
    template_name = 'nuka/messages.html'

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        obj = self.kwargs['obj']
        obj.approve(self.request.user)
        ContentFlag.objects.filter(
            content_type=obj.content_type,
            object_id=obj.object_pk,
            status=ContentFlag.STATUS_FLAGGED
        ).update(
            status=ContentFlag.STATUS_FLAG_REJECTED,
            updated=timezone.now()
        )
        obj.moderator.approve_object(obj, moderator=self.request.user)
        messages.success(self.request, _("Sisältö hyväksytty."))
        return self.render_to_response({})


class RejectModeratedObject(TemplateResponseMixin, View):
    template_name = 'nuka/messages.html'

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        obj = self.kwargs['obj']
        obj.moderated_by = request.user
        obj.moderation_status = MODERATION_STATUS_REJECTED
        obj.moderation_date = timezone.now()
        obj.save()
        obj.moderator.reject_object(obj, moderator=request.user)
        messages.warning(self.request, _("Sisältö poistettu."))
        return self.render_to_response({})
