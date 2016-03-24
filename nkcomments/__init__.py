from django.core.urlresolvers import reverse
from nkcomments.models import CustomComment


def get_model():
    return CustomComment


def get_form_target():
    return reverse('nkcomments:post-comment')