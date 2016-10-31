from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from django.views.generic.base import RedirectView


class SlugRedirect(RedirectView):
    model = None

    def get_redirect_url(self, *args, **kwargs):
        if not self.model:
            if not kwargs.get('model', None):
                raise Http404()
            self.model = kwargs.pop('model')
        pk = kwargs.pop('pk')
        obj = get_object_or_404(self.model, pk=pk)
        return obj.get_absolute_url(get_language())
