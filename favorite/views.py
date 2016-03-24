from django.contrib.contenttypes.models import ContentType
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.template.response import TemplateResponse
from django.views.generic.list import ListView
from account.models import User
from favorite.forms import UserFavoriteTagForm, UserFavoriteOrganizationForm
from django.http import JsonResponse
from django.core.urlresolvers import reverse

from .models import Favorite


class FavoriteBaseUpdateView(UpdateView):

    def get_object(self):
        return Favorite.objects.filter(user_id=self.request.user.pk,
                                       content_type_id=self.kwargs['content_type_id'],
                                       object_id=self.kwargs['object_id']).first()

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return False

        if self.get_object():
            self.unfollow()
        else:
            self.follow()
        # TODO: wrong return value !!!
        return True

    def follow(self):
        Favorite.objects.create(
            user_id=self.request.user.pk,
            content_type_id=self.kwargs['content_type_id'],
            object_id=self.kwargs['object_id']
        )

    def unfollow(self):
        obj = self.get_object()
        obj.delete()


class AddOrRemoveIdeaView(FavoriteBaseUpdateView):

    def post(self, request, *args, **kwargs):
        super(AddOrRemoveIdeaView, self).post(request, *args, **kwargs)

        return TemplateResponse(request, 'favorite/follow_idea_link.html',
                                self.get_template_attribute_objects())

    def get_template_attribute_objects(self):
        ct = ContentType.objects.get(pk=self.kwargs['content_type_id'])
        return {
            'obj': ct.get_object_for_this_type(pk=self.kwargs['object_id']),
            'ct': ct
        }


class UserFavoriteEditView(UpdateView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'favorite/favorite_edit.html'
    TYPE_TAG = 'tagging.tag'
    TYPE_ORGANIZATION = 'organization.organization'
    FORM_CLASSES = {
        TYPE_TAG: UserFavoriteTagForm,
        TYPE_ORGANIZATION: UserFavoriteOrganizationForm,
    }

    def get_form_class(self):
        ct = ContentType.objects.get_for_id(self.kwargs['ct_id'])
        return self.FORM_CLASSES["{0}.{1}".format(ct.app_label, ct.model)]

    def get_success_url(self):
        return reverse('favorite:favorite_detail', kwargs={
                'user_id': self.kwargs['user_id'],
                'ct_id': self.kwargs['ct_id']
            })

    def form_valid(self, form):
        super(UserFavoriteEditView, self).form_valid(form)

        return JsonResponse({
            'success': True,
            'next': self.get_success_url()
        })


class UserFavoriteDetailView(DetailView):
    template_name = 'favorite/favorite_detail.html'

    def get_object(self):
        return User.objects.get(pk=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        context = super(UserFavoriteDetailView, self).get_context_data()
        context['user'] = self.get_object()
        context['ct_id'] = self.kwargs['ct_id']
        return context