from django.db import transaction
from collections import OrderedDict
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.messages.api import add_message
from django.http.response import HttpResponseRedirect
from django.utils.encoding import force_text
from django.views.generic.base import RedirectView, ContextMixin, TemplateResponseMixin, View


class FlashRedirectView(RedirectView):
    permanent = False
    message = None
    message_type = None

    def get_redirect_url(self, *args, **kwargs):
        add_message(self.request, self.message_type or constants.SUCCESS, self.message)
        return super(FlashRedirectView, self).get_redirect_url(*args, **kwargs)


class FormMessagesMixIn(object):
    success_msg = None
    error_msg = None

    def get_success_msg(self):
        return self.success_msg

    def get_error_msg(self):
        return self.error_msg

    def show_success_msg(self):
        msg = self.get_success_msg()
        if msg is not None:
            messages.success(self.request, msg)

    def show_error_msg(self):
        msg = self.get_error_msg()
        if msg is not None:
            messages.error(self.request, msg)

    def form_valid(self, *args, **kwargs):
        resp = super(FormMessagesMixIn, self).form_valid(*args, **kwargs)
        self.show_success_msg()
        return resp

    def form_invalid(self, *args, **kwargs):
        resp = super(FormMessagesMixIn, self).form_invalid(*args, **kwargs)
        self.show_error_msg()
        return resp


class MultiFormView(ContextMixin, TemplateResponseMixin, View):
    # tuple of two-tuples ((<kwarg>, <getter_postfix>),)
    form_kwarg_getters = (
        ('initial', 'initial'),
    )
    # tuple of two-tuples ((<prefix>, <form_class>),)
    form_classes = ()

    def __init__(self, *args, **kwargs):
        self.forms = OrderedDict()
        super(MultiFormView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['forms'] = self.forms.copy()
        return kwargs

    def get_form_kwargs(self, prefix):
        kwargs = {'prefix': prefix or None,}

        for kw,postfix in self.form_kwarg_getters:
            getter = 'get_%s_%s' % (prefix, postfix)
            if hasattr(self, getter):
                kwargs[kw] = getattr(self, getter)()

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        kwargs_getter = getattr(self, 'get_%s_form_kwargs' % prefix, None)
        if kwargs_getter is not None:
            kwargs = kwargs_getter(kwargs)
        return kwargs

    def get_form_classes(self):
        return self.form_classes

    def post(self, *args, **kwargs):
        all_valid = True
        for prefix, klass in self.get_form_classes():
            self.forms[prefix] = klass(**self.get_form_kwargs(prefix))
            if not self.forms[prefix].is_valid():
                all_valid = False
        if all_valid:
            return self.form_valid()
        else:
            return self.form_invalid()

    def form_invalid(self):
        """
        At least one of the forms didn't validate.
        """
        return self.render_to_response(self.get_context_data())

    def get(self, *args, **kwargs):
        for prefix, klass in self.get_form_classes():
            self.forms[prefix] = klass(**self.get_form_kwargs(prefix))
        return self.render_to_response(self.get_context_data())

    def form_valid(self):
        """
        All of the forms validated.
        """
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        Copy-pasted from django.views.generic.edit.FormMixIn. Not inheriting
        from it, because it would provide confusing methods.
        """
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            url = force_text(self.success_url)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url


class MultiModelFormView(MultiFormView):
    form_kwarg_getters = MultiFormView.form_kwarg_getters + (
        ('instance', 'object'),
    )

    def __init__(self, *args, **kwargs):
        self.objects = {}
        super(MultiModelFormView, self).__init__(*args, **kwargs)

    def save_forms(self):
        for prefix,form in self.forms.iteritems():
            presaver = 'presave_%s' % prefix
            postsaver = 'postsave_%s' % prefix
            if hasattr(self, presaver):
                self.objects[prefix] = form.save(commit=False)
                getattr(self, presaver)(obj=self.objects[prefix])
                self.objects[prefix].save()
            else:
                self.objects[prefix] = form.save()
            if hasattr(self, postsaver):
                getattr(self, postsaver)(obj=self.objects[prefix])
        if hasattr(self, 'postsave'):
            self.postsave()

    @transaction.atomic()
    def form_valid(self):
        self.save_forms()
        return super(MultiModelFormView, self).form_valid()


class SortableMixin(object):
    sort_param = 'sort'
    sort_fields = ()
    sort_class_asc = 'asc'
    sort_class_desc = 'desc'
    active_sort = None
    active_sort_field = None
    default_sorting = None

    def _sort_by(self, qs, sorting):
        self.active_sort = sorting
        self.active_sort_field = sorting.lstrip('-')
        self.active_sort_desc = sorting[0] == '-'
        return qs.order_by(sorting)

    def get_queryset(self):
        qs = super(SortableMixin, self).get_queryset()
        sorting = self.request.GET.get(self.sort_param, '')

        for f in self.sort_fields:
            if sorting in (f, '-' + f):
                return self._sort_by(qs, sorting)

        if self.default_sorting is not None:
            return self._sort_by(qs, self.default_sorting)

        return qs

    def get_context_data(self, **kwargs):
        kwargs = super(SortableMixin, self).get_context_data(**kwargs)
        sort_classes, sort_urls = {}, {}
        q = self.request.GET.copy()

        for f in self.sort_fields:
            if self.active_sort_field == f:
                q[self.sort_param] = f if self.active_sort_desc else '-' + f
                sort_classes[f] = self.sort_class_desc if self.active_sort_desc \
                    else self.sort_class_asc
            else:
                q[self.sort_param] = f
            sort_urls[f] = '?'.join([self.request.path, q.urlencode()])

        kwargs.update({
            'sort_urls': sort_urls,
            'sort_classes': sort_classes
        })

        return kwargs
