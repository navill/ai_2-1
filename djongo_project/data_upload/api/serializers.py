from rest_framework import serializers

from accounts.constants import User
from data_upload.models import CommonFile


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    from_user = serializers.CharField()
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

    class Meta:
        model = CommonFile
        fields = ['file', 'from_user', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        super().to_internal_value(data)
        username = User.objects.get(username=data['from_user'])
        result = {
            'from_user': username,
            'file': data['file'],
        }
        return result
