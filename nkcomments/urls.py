# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from content.models import Initiative
from content.perms import CanCommentInitiative

from libs.djcontrib.conf.urls import decorated_patterns
from libs.djcontrib.utils.decorators import combo, obj_by_pk
from libs.permitter.decorators import check_perm
from nkcomments.perms import CanEditComment

from nkvote.models import Vote

from . import views
from .models import CustomComment
from .perms import CanVoteComment, CanDeleteComment


urlpatterns = patterns('django_comments.views',
    url(r'^(?P<initiative_id>\d+)/post/$', combo(obj_by_pk(Initiative, "initiative_id"),
                          check_perm(CanCommentInitiative))(views.post_comment), name='post-comment'),
)

# Votes
urlpatterns += decorated_patterns(
    "",
    combo(obj_by_pk(CustomComment, "comment_id"), check_perm(CanVoteComment)),
    url(
        r'^(?P<comment_id>\d+)/kannata/$',
        views.VoteCommentView.as_view(choice=Vote.VOTE_UP),
        name="support_comment"
    ),
    url(
        r'^(?P<comment_id>\d+)/vastusta/$',
        views.VoteCommentView.as_view(choice=Vote.VOTE_DOWN),
        name="oppose_comment"
    )
)

# Comment deletion/edit
urlpatterns += decorated_patterns(
    '',
    obj_by_pk(CustomComment, 'pk'),
    url(r'^(?P<pk>\d+)/poista/$',
        check_perm(CanDeleteComment)(views.DeleteCommentView.as_view()),
        name='delete_comment'
    ),
    url(r'^(?P<pk>\d+)/muokkaa/$',
        check_perm(CanEditComment)(views.EditCommentView.as_view()),
        name='edit_comment'
    ),
    url(r'^(?P<pk>\d+)/nayta/$',
        # only needed after editing a comment (for now at least)
        check_perm(CanEditComment)(views.CommentContentView.as_view()),
        name='view_comment'
    ),
)