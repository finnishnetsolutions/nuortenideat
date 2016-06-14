# dependencies
# django-image-cropping
# easy-thumbnails

from easy_thumbnails.files import get_thumbnailer


class CroppingModelMixin(object):

    crop_connect_field = 'original_picture'
    crop_field = 'picture'
    cropping_field = 'cropping'
    cropping = None
    picture = None
    # cropping_pk_field used in EditCroppablePictureView when updating cropping field
    # usable when cropping field in related model
    cropping_pk_field = 'pk'

    def save(self):
        raise NotImplementedError

    def get_cropped_dimensions(self):
        height = 0
        width = 0
        cropping = getattr(self, self.cropping_field)
        if cropping:
            crops = cropping.split(',')
            height = int(crops[3]) - int(crops[1])
            width = int(crops[2]) - int(crops[0])
        return [height, width]

    def crop(self):
        # delete old picture
        self.__getattribute__(self.crop_field).delete()

        # crop picture
        cropped = get_thumbnailer(
            self.__getattribute__(self.crop_connect_field)).get_thumbnail(
            {
                'size': self.get_cropped_dimensions(),
                'box': getattr(self, self.cropping_field),
                'crop': True,
                'detail': True,
            }
        )

        # save cropped picture
        setattr(self, self.crop_field, cropped.name)
        self.save()

    def copy_to_crop_connect_field(self):
        setattr(self, self.crop_connect_field,
                self.__getattribute__(self.crop_field).file)

    def get_template_cancel_url(self):
        raise NotImplementedError

# TODO post_delete signal for emptying cropping field and removing cropped picture
