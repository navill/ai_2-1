from rest_framework import serializers

from accounts.constants import User
from files.models import CommonFile


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()  # file list
    from_user = serializers.CharField()
    # to_user = serializers.CharField()

    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

    # DOC, IMG, WAV로 파일 분류
    # DOC = (...)
    # IMG = (...)
    # WAV = (...)
    FILE_EXTENSION = ('doc', 'md', 'hwp', 'pdf', 'xls')

    class Meta:
        model = CommonFile
        fields = ['file', 'from_user', 'created_at', 'updated_at']

    def to_internal_value(self, data: dict) -> dict:
        super().to_internal_value(data)

        username = User.objects.get(username=data['from_user'])

        result = {
            'from_user': username,
            'file': data['file'],
        }
        return result

# FileUploadParser
    def validate(self, attrs: dict) -> dict:
        vals = super().validate(attrs)
        _, extension = str(vals['file']).split('.')

        if extension in self.FILE_EXTENSION:
            pass
        return vals