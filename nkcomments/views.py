# coding=utf-8

from __future__ import unicode_literals

from django.apps import apps
from django.contrib import messages
from django.contrib.comments import signals
from django.contrib.comments.views.comments import CommentPostBadRequest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.html import escape
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from content.models import Initiative
from libs.attachtor.forms.forms import RedactorAttachtorFormMixIn
from nkcomments.forms import CommentEditForm, AnonCommentEditForm
from nkmoderation.utils import get_moderated_form_class
from nkvote.models import Vote, Voter
from nkvote.utils import vote, set_vote_cookie, get_votes

from .utils import get_form
from . import perms

from nkcomments.models import CustomComment, CommentUserOrganisations


@csrf_protect
@require_POST
def post_comment(request, next=None, using=None, **kwargs):
    """
    Post a comment.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comments/preview.html``, will be rendered.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = apps.get_model(ctype)
        target = model._default_manager.using(using).get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except LookupError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % \
                escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % \
                (escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError) as e:
        return CommentPostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % \
                (escape(ctype), escape(object_pk), e.__class__.__name__))

    # Construct the comment form
    form = get_form(request, target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % \
                escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the comment
    if not form.is_valid():
        return render_to_response(
            'nkcomments/comment_form.html', {
                'object': target,
                "comment": form.data.get("comment", ""),
                'form': form,
                "next": data.get("next", next),
            },
            RequestContext(request, {})
        )

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    premoderation = getattr(comment.content_object, 'premoderation', False)

    if premoderation:
        comment.is_public = False

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    for (receiver, response) in responses:
        if response == False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()

    if comment.user:
        user_orgs = set(comment.user.organization_ids)
        idea_orgs = set(comment.content_object.target_organization_ids)
        for o_id in user_orgs & idea_orgs:
            CommentUserOrganisations(comment_id=comment.pk, organization_id=o_id).save()

    signals.comment_was_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    model_name = 'idea' if model.__name__ == 'Idea' else 'question'

    if premoderation:
        messages.success(request, ugettext(
            "Kommenttisi on tallennettu. Kommentti tulee näkyviin, kun moderaattori on "
            "hyväksynyt sen."))

    return JsonResponse({'success': True,
                         'next': reverse('content:comment_block_%s' % model_name, kwargs={
                             'initiative_id': target.pk})})


class CommentBlockView(TemplateView):
    template_name = 'nkcomments/comment_block.html'
    model = None
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        initiative = get_object_or_404(self.model, pk=self.kwargs[self.pk_url_kwarg])

        if self.request.user.is_authenticated() and self.request.user.is_moderator:
            comments = initiative.public_comments()
        else:
            comments = initiative.public_comments().public()

        kwargs['object'] = initiative
        kwargs['comments'] = comments
        kwargs["comment_votes"] = get_votes(
            self.request, CustomComment, comments
        )
        return kwargs


class VoteCommentView(TemplateView):
    http_method_names = ["post"]
    template_name = "nkcomments/comment_list_item.html"
    choice = Vote.VOTE_DOWN

    def post(self, request, *args, **kwargs):
        comment = CustomComment.objects.get(pk=self.kwargs["comment_id"])

        context = self.get_context_data()
        context["comment"] = comment
        context["comment_vote"] = vote(request, CustomComment, comment.pk, self.choice)
        context["deleted"] = comment.is_deleted()
        context["object"] = Initiative.objects.get(pk=comment.object_pk)

        # Set the cookie for voting.
        response = super(VoteCommentView, self).render_to_response(context)
        try:
            voter_id = context["comment_vote"].voter.voter_id
        except AttributeError:
            voter_id = None

        # needs to set cookie for request too. permission checks will then have fresh data
        self.request.COOKIES[Voter.VOTER_COOKIE] = voter_id
        return set_vote_cookie(request, response, voter_id)


class DeleteCommentView(TemplateView):
    """ Marks the comment deleted by given pk and returns the given template
        with the comment. Used for ajaxy requests. """
    pk_url_kwarg = "pk"
    http_method_names = ["post"]
    template_name = "nkcomments/comment_list_item.html"

    def delete(self, request, **kwargs):
        comment = CustomComment.objects.get(pk=self.kwargs[self.pk_url_kwarg])
        comment.mark_deleted(request.user)
        object = Initiative.objects.get(pk=comment.object_pk)
        return self.render_to_response(
            {"comment": comment, "deleted": True, "object": object}
        )

    def post(self, request, **kwargs):
        return self.delete(request, **kwargs)


class EditCommentView(UpdateView):
    model = CustomComment
    template_name = 'nkcomments/comment_edit_form.html'

    def get_form_class(self):
        obj = self.kwargs['obj']
        klass = AnonCommentEditForm if obj.user_id is None else CommentEditForm
        if not perms.OwnsComment(
            request=self.request,
            obj=self.get_object()
        ).is_authorized():
            return get_moderated_form_class(klass, self.request.user)
        return klass

    def form_valid(self, form):
        obj = form.save()
        return JsonResponse({'success': True,
                             'next': reverse('nkcomments:view_comment',
                                             kwargs={'pk': obj.pk})})


class CommentContentView(DetailView):
    model = CustomComment
    template_name = 'nkcomments/comment_content.html'
    context_object_name = 'comment'

    def get_context_data(self, **kwargs):
        ctx = super(CommentContentView, self).get_context_data(**kwargs)
        ctx.update({
            'object': ctx['comment'].content_object,
        })
        return ctx
