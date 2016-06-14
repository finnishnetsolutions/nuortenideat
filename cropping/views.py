from django.db import transaction
from django.http.response import HttpResponseRedirect
from django.views.generic.edit import FormView


class BaseCropFormView(FormView):
    def get_success_url(self):
        # TODO: use get_absolute_url if get_cropping_cancel_url not defined
        return self.get_object().get_cropping_cancel_url()


class CropPictureView(BaseCropFormView):
    template_name = 'cropping/crop_form.html'
    form_class = None

    @transaction.atomic
    def form_valid(self, form):
        obj = form.save()
        obj.crop()
        return HttpResponseRedirect(self.get_success_url())


class EditCroppablePictureView(BaseCropFormView):

    @transaction.atomic
    def form_valid(self, form):
        obj = form.save()

        # "wake up" simple lazy objects
        if hasattr(obj, '_wrapped') and hasattr(obj, '_setup'):
            if obj._wrapped.__class__ == object:
                obj._setup()
            obj = obj._wrapped

        obj.copy_to_crop_connect_field()
        obj.save()

        # skip cropping. using update because of crop field pre-save signal
        model = type(obj)
        model.objects.filter(**{obj.cropping_pk_field: self.get_object().pk}).\
            update(cropping='')
        return HttpResponseRedirect(self.get_success_url())
