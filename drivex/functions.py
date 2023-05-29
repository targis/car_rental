from django.utils.deconstruct import deconstructible
import os


@deconstructible
class UploadToPathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(instance.name, ext)
        if instance.brand:
            return os.path.join(self.path, instance.brand.name, filename)
        else:
            return os.path.join(self.path, filename)
