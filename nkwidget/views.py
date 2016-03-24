# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import activate

from content.models import Idea
from content.views import ListAndSearchView
from nkwidget.forms import WidgetIdeaForm


class ShowWidgetView(ListAndSearchView):
    template_name = "nkwidget/initiative/initiative_list.html"
    form_class = WidgetIdeaForm
    queryset = Idea._default_manager.get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ShowWidgetView, self).get_context_data(**kwargs)
        if hasattr(self.searchform, "cleaned_data"):
            context["color"] = self.searchform.cleaned_data.get(
                "color", self.searchform.DEFAULT_COLOR
            )
            context["language"] = self.searchform.cleaned_data.get(
                "language", self.searchform.DEFAULT_LANGUAGE
            )
        if not context.get("language") or not context["language"]:
            context["language"] = self.searchform.DEFAULT_LANGUAGE
        activate(context["language"])
        context["errors"] = self.searchform.errors
        return context
