from typing import *

from rest_framework import serializers
from rest_framework.reverse import reverse

from accounts.models import CommonUser
from utilities.file_utils import EncryptHandler
from files.models import CommonFile


class FileManageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CommonUser.objects.all(), required=False)
    patient_name = serializers.CharField(required=True)
    file = serializers.FileField(use_url=False)
    raw_file = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = CommonFile
        fields = ['user', 'patient_name', 'file', 'raw_file', 'created_at']

    def to_representation(self, instance: CommonFile) -> Dict:
        ret = super().to_representation(instance)
        encrypted_path = self._create_encrypted_path(str(instance.id))
        encrypted_pull_url = reverse('files:download', args=[encrypted_path], request=self.context['request'])
        ret['url'] = encrypted_pull_url
        if hasattr(instance, 'user'):
            ret['user'] = instance.user.username
        return ret

    def create(self, validated_data: dict) -> CommonFile:
        try:
            file_obj = CommonFile.objects.create(**validated_data)
        except Exception:
            raise
        return file_obj

    def _create_encrypted_path(self, instance_id: str) -> str:
        handler = EncryptHandler(instance_id)
        return handler.encrypt()
