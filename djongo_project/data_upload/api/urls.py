from django.urls import path

from data_upload.api.views import FileUploadView

app_name = 'data_upload'
urlpatterns = [
    path('file/', FileUploadView.as_view())
]
