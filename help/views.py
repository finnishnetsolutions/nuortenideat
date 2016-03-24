# coding=utf-8

from __future__ import unicode_literals

from operator import attrgetter
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView

from .models import Instruction


class InstructionDetailFirst(RedirectView):
    pattern_name = 'help:instruction_detail'

    def get_redirect_url(self, *args, **kwargs):
        obj = Instruction.objects.first()
        if obj is None:
            raise Http404()
        return super(InstructionDetailFirst, self).get_redirect_url(pk=obj.pk)


class InstructionDetail(ListView):
    model = Instruction
    template_name = 'help/instruction_list.html'

    def get_context_data(self, **kwargs):
        context = super(InstructionDetail, self).get_context_data(**kwargs)
        context['selected_instruction'] = get_object_or_404(
            Instruction, pk=self.kwargs['pk'])
        return context


class LinkedInstructionRedirectView(RedirectView):
    pattern_name = 'help:instruction_detail'

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Instruction, connect_link_type=self.kwargs['slug'])
        return super(LinkedInstructionRedirectView, self).get_redirect_url(pk=obj.pk)