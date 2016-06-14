from imagekit.models.fields import ProcessedImageField
from cropping.widgets import ImageCropWidget


class ProcessedImageFieldWithCropping(ProcessedImageField):
    def formfield(self, **kwargs):
        defaults = {'widget': ImageCropWidget}
        defaults.update(kwargs)
        return super(ProcessedImageFieldWithCropping, self).formfield(**defaults)
