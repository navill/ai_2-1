import datetime

from djongo import models

from accounts.models import CommonUser


def user_directory_path(instance: 'CommonFile', filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    name, ext = filename.split('.')
    return f'{day}/{instance.user}/{instance.patient_name}/{name}_{time}.{ext}'


class FileQueryManager(models.QuerySet):
    def owner(self, user):
        if user.is_admin:
            return self
        return self.filter(user.id)


class FileManager(models.Manager):
    def get_queryset(self):
        print(1)
        return FileQueryManager(self.model, using=self._db)

    def owner(self, user):
        print(2)
        return self.get_queryset().owner(user)


class CommonFile(models.Model):
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    file_objects = FileManager()

    def __str__(self):
        return str(self.user)

    def is_owner(self, user):
        if self.user == user.id:
            return True
        return False
