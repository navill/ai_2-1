from datetime import datetime

from django.db import models

from accounts.constants import User


def file_upload_to(instance, filename):
    return create_path(instance, filename)


def create_path(instance, filename):
    name = instance.from_user.username
    now = datetime.now().strftime('%Y-%m-%d')

    basename, file_extension = filename.split(".")
    new_filename = f"{name}_{basename}.{file_extension}"
    return f"dir_files/{now}/{name}/{new_filename}"


class CommonFile(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_upload_to, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file.name
