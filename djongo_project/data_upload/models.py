from datetime import datetime

from django.db import models

# Create your models here.
from accounts.constants import User


def file_upload_to(instance, filename):
    name = instance.from_user.username
    now = datetime.now().strftime('%Y-%m-%d')
    basename, file_extension = filename.split(".")
    new_filename = f"{name}-{instance.from_user.id}.{file_extension}"
    return f"dir_files/{now}/{name}/{new_filename}"


class CommonFile(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_upload_to, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    RENAME_FILES = {
        'file': {'dest': 'media/files', 'keep_ext': True}
    }

    def __str__(self):
        return self.file.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(CommonFile, self).save(force_insert=force_insert, force_update=force_update)
