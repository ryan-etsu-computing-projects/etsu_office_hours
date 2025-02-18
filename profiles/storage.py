from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        """Returns a filename that's free on the target storage system.

        If the file already exists, it will delete it first.
        """
        # If the filename already exists, remove it
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name