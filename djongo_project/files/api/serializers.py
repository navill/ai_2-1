from rest_framework import serializers
from rest_framework.reverse import reverse

from accounts.models import CommonUser
from files.api.utils import URLHandler
from files.models import CommonFile


class FileManageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CommonUser.objects.all(), required=False)
    patient_name = serializers.CharField(required=True)
    file = serializers.FileField(use_url=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = CommonFile
        fields = ['user', 'patient_name', 'file', 'created_at']
        read_only_fields = ['user']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        encrypted_path = self._create_encrypted_path(str(instance.id))
        ret['url'] = reverse('files:download', args=[encrypted_path], request=self.context['request'])
        return ret

    def create(self, validated_data: dict):
        try:
            file_obj = CommonFile.objects.create(**validated_data)
        except Exception:
            raise
        return file_obj

    def _create_encrypted_path(self, instance_id: str) -> str:
        handler = URLHandler(instance_id)
        return handler.encrypt_to_str()
