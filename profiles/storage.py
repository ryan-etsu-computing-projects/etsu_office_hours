from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        """
        If the file with name already exists, delete it first.
        Then return the name to use for saving the new file.
        """
        # Check if the file exists on disk
        if self.exists(name):
            file_path = os.path.join(settings.MEDIA_ROOT, name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
                
        return name