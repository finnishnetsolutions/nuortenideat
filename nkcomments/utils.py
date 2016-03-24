from nkcomments.forms import CustomCommentForm, CustomCommentFormAnon


def get_form(request, *args, **kwargs):
    if request.user.is_authenticated():
        klass = CustomCommentForm
    else:
        klass = CustomCommentFormAnon
    return klass(*args, **kwargs)
