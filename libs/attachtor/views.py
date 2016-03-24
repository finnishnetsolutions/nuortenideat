# coding=utf-8

from __future__ import unicode_literals

from django.db import transaction
from django.http.response import JsonResponse, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView

from libs.attachtor.decorators import validate_upload_token
from libs.attachtor.models import UploadGroup

from .forms.forms import FileUploadForm


class UploadAttachmentView(CreateView):
    form_class = FileUploadForm

    @method_decorator(csrf_exempt)
    @method_decorator(validate_upload_token)
    def dispatch(self, request, *args, **kwargs):
        return super(UploadAttachmentView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed()

    @transaction.atomic()
    def form_valid(self, form):
        upload = form.save(commit=False)
        upload.group, created = UploadGroup.objects.get_or_create(
            pk=self.kwargs['upload_group_id']
        )
        if self.request.user.is_authenticated():
            upload.uploader = self.request.user
        upload.original_name = upload.file.file.name
        upload.size = upload.file.file.size
        upload.save()
        return JsonResponse({'filelink': upload.file.url,
                             'filename': upload.original_name, })

    def form_invalid(self, form):
        return JsonResponse({'error': ugettext("Upload failed"), 'debug': form.errors})
