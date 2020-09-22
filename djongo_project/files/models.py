import datetime

from djongo import models

from accounts.models import CommonUser


def user_directory_path(instance: 'CommonFile', filename: str) -> str:
    day, time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S').split('_')
    name, ext = filename.split('.')
    return f'{day}/{instance.user}/{instance.patient_name}/{name}_{time}.{ext}'


class CommonFile(models.Model):
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

    def is_owner(self, user):
        if self.user == user:
            return True
        return False
